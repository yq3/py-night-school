#!/usr/bin/env python3
"""三态验证法（AGENTS.md §5）的自动化：发货态 / 毕业态 / 机器校验。

用法：
    python3 scripts/three_state_check.py units/unit2-mini-agent/L2.1-raw-api   # 单课（可多个）
    python3 scripts/three_state_check.py                                      # 全量：30 课时 + 5 里程碑

Windows 注意：python3 常是 Store 存根（退出码 49 打不开），换 python 或 py -3 调用本脚本。

对每个课时目录做三件事：
1. 发货态：原地跑三命令（pytest / ruff check / pyright）——三条命令同口径：设计内红
   （TODO 未填的 FAILED、学员作答区的 lint 违规与类型 error）必须全部落在学员作答区，
   code/ 讲义区必须绿；
2. 毕业态：把课时目录镜像到系统临时目录（保持仓库相对深度，data/ 一并镜像，
   这样引用共享素材的测试不断粮），用 solution/ex*.py 覆盖 exercises/ 后跑三命令
   + ruff format --check——全部通过；
3. 提醒 check_lesson.py 的结果（结构校验）。

仅用标准库 + 课时自身的 uv。exit 0 = 三态全过。
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THREE_COMMANDS = ("pytest", "ruff check .", "pyright")

# ruff 违规定位行的两种输出形态（默认 full 与 --output-format concise）：
# concise：`路径:行:列: CODE 提示`；full：诊断正文下一行的 `  --> 路径:行:列`
RUFF_LOCATION_RES = (
    re.compile(r"^(\S+?):\d+:\d+: [A-Z]+\d+ "),
    re.compile(r"^\s*--> (\S+):\d+:\d+\s*$"),
)

# pytest 自己的结果行：`FAILED 路径…` / `ERROR 路径…`（含 `ERROR collecting 路径`）——
# 恰一个空格后跟内容。第三方库日志行（如 adk 的「ERROR    google_adk…」多空格对齐）
# 不匹配，不能让它触发或绕过判定（先例：L3.6 全绿误判 FAIL）。
PYTEST_RESULT_RE = re.compile(r"^(FAILED|ERROR) \S")

# pyright 的违规定位行：`路径:行:列 - error: 提示`
PYRIGHT_ERROR_RE = re.compile(r"^\s*(\S+?):\d+:\d+ - error: ")


def _in_allowed(path: str, allowed: str) -> bool:
    """路径是否落在学员作答区内——前缀判定且带分隔符。

    整行子串包含会误放行（先例：`FAILED code/… - AssertionError: exercises != []`
    里的「exercises」一词掩护讲义区的红——外部评审 P1）；不带分隔符的前缀会把
    `exercises_extra/` 误认进 exercises/。Windows 反斜杠形态一并覆盖。
    """
    return path.startswith(f"{allowed}/") or path.startswith(f"{allowed}\\")


def run(cmd: str, cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(f"uv run {cmd}", shell=True, cwd=cwd, capture_output=True, text=True)
    return completed.returncode, completed.stdout + completed.stderr


def is_designed_failure(output: str, lesson: Path) -> bool:
    """发货态的「精确红」：pytest 摘要里 FAILED 行全部落在学员作答区——课时是 exercises/，里程碑是 tests/。

    只认 FAILED（用例失败）这一种设计内红；任何 ERROR 行（集合错误）都意味着 import/骨架
    已损坏，不是 TODO 未填的预期形态——出现即整体判 FAIL，不被设计内红掩护。
    """
    lines = output.splitlines()
    # ERROR 结果行（集合错误，含 short summary 与「ERROR collecting」）一律视为骨架损坏：
    # 哪怕练习区同时有设计内 FAILED，也不许被它掩护着混过（先例：2026-09-21 评审发现
    # 混合摘要被误判为设计内失败）。只认 pytest 自己的结果行——库日志的 ERROR 不算数。
    result_lines = [line for line in lines if PYTEST_RESULT_RE.match(line)]
    if any(line.startswith("ERROR") for line in result_lines):
        return False
    failed_lines = [line for line in result_lines if line.startswith("FAILED")]
    if not failed_lines:
        return False
    if (lesson / "exercises").is_dir():
        allowed = "exercises"
    elif (lesson / "tests").is_dir():
        allowed = "tests"
    else:
        return False
    for line in failed_lines:
        # `FAILED 路径[::测试] - 消息`——只取路径段做前缀判定，消息文本不参与
        node = line.split(" ", 1)[1]
        path = node.split("::")[0].split(" - ")[0].removeprefix("./")
        if not _in_allowed(path, allowed):
            return False
    return True


def is_designed_ruff_failure(output: str, lesson: Path) -> bool:
    """发货态 ruff 的「精确红」：全部违规行都落在学员作答区，才认设计内违规。

    先例：L0.1 ex3 的 E501 出在单字符串字面量上——ruff format 出于语义安全不改写
    字符串内容，这处违规必须由学生手工拆，发货态天然带红（宪法 §5「ex3 类设计内
    ruff 违规」）。讲义区 code/ 的任何违规照常判 FAIL。
    """
    violations = [
        path.removeprefix("./")
        for pattern in RUFF_LOCATION_RES
        for path in (m.group(1) for m in map(pattern.match, output.splitlines()) if m)
    ]
    if not violations:
        return False  # 定位行都解析不出（输出形态再变等）——不认设计内红，保守判 FAIL
    if (lesson / "exercises").is_dir():
        allowed = "exercises"
    elif (lesson / "tests").is_dir():
        allowed = "tests"
    else:
        return False
    return all(_in_allowed(path, allowed) for path in violations)


def is_designed_pyright_failure(output: str, lesson: Path) -> bool:
    """发货态 pyright 的「精确红」：全部 error 定位行都落在学员作答区，才认设计内红。

    先例：L1.2 / L1.3 的验收测试访问学员尚未实现的属性 / 字段（TODO 未填的天然形态，
    毕业态覆盖 solution 后即绿）——与 pytest FAILED、ruff 违规同口径。定位不到 error
    行（输出形态变化、或配置级错误无路径）时保守判 FAIL。
    """
    error_paths = [m.group(1) for m in map(PYRIGHT_ERROR_RE.match, output.splitlines()) if m]
    if not error_paths:
        return False
    if (lesson / "exercises").is_dir():
        allowed = "exercises"
    elif (lesson / "tests").is_dir():
        allowed = "tests"
    else:
        return False
    for raw in error_paths:
        path = Path(raw)
        if path.is_absolute():
            try:  # 课时外的 error（如 site-packages）不算设计内红
                path = path.relative_to(lesson.resolve())
            except ValueError:
                return False
        if not _in_allowed(str(path), allowed):
            return False
    return True


def check_one(lesson: Path) -> bool:
    """对单个课时/里程碑目录跑三态，返回是否全过。"""
    failures: list[str] = []

    # ---- 1. 发货态 ----
    print(f"== 发货态 {lesson.relative_to(ROOT)} ==")
    for cmd in THREE_COMMANDS:
        code, output = run(cmd, lesson)
        if cmd.startswith("pytest"):
            ok = code == 0 or is_designed_failure(output, lesson)
            detail = "（练习区设计内红）" if code != 0 and ok else ""
            print(f"  uv run {cmd:<14} -> {'PASS' if ok else 'FAIL'} {detail}")
            if not ok:
                failures.append(f"发货态 {cmd} 出现设计外的红")
        elif cmd.startswith("ruff check"):
            ok = code == 0 or is_designed_ruff_failure(output, lesson)
            detail = "（练习区设计内 lint 违规）" if code != 0 and ok else ""
            print(f"  uv run {cmd:<14} -> {'PASS' if ok else 'FAIL'} {detail}")
            if not ok:
                failures.append(f"发货态 {cmd} 出现设计外的红")
        elif cmd.startswith("pyright"):
            ok = code == 0 or is_designed_pyright_failure(output, lesson)
            detail = "（练习区设计内类型红）" if code != 0 and ok else ""
            print(f"  uv run {cmd:<14} -> {'PASS' if ok else 'FAIL'} {detail}")
            if not ok:
                failures.append(f"发货态 {cmd} 出现设计外的红")
        else:
            print(f"  uv run {cmd:<14} -> {'PASS' if code == 0 else 'FAIL'}")
            if code != 0:
                failures.append(f"发货态 {cmd} 非绿")

    # ---- 2. 毕业态（临时目录镜像，保持仓库内相对深度） ----
    print("== 毕业态（solution 覆盖后的临时副本） ==")
    with tempfile.TemporaryDirectory(prefix="pns-grad-") as tmp:
        mirror_root = Path(tmp) / "mirror"
        # 相对深度：py-night-school/<unit>/<lesson> —— 镜像同样三层
        unit_dir = lesson.parent.relative_to(ROOT)
        dest = mirror_root / "py-night-school" / unit_dir / lesson.name
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            lesson,
            dest,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".venv", ".pytest_cache", ".ruff_cache", "__pycache__"),
        )
        # 共享素材：data/ 与课时目录同层数（parents[4] 的解析目标）
        shutil.copytree(ROOT / "data", mirror_root / "py-night-school" / "data")
        # solution 覆盖学员作答区：课时 -> exercises/，里程碑（无 exercises/）-> 目录根。
        # 递归覆盖（先例：L1.1 的答案在 solution/claimfix/runner.py 嵌套包里，
        # 顶层 glob 漏拷导致毕业态误判 FAIL——2026-09-21 评审发现）。
        overlay = dest / "solution"
        if overlay.is_dir():
            target_dir = dest / "exercises" if (dest / "exercises").is_dir() else dest
            for solution_file in overlay.rglob("*.py"):
                target = target_dir / solution_file.relative_to(overlay)
                if target.is_file():
                    shutil.copy2(solution_file, target)
                else:
                    # 教材侧错位可见化（外部评审 P2）：solution 多出/改名的文件静默漂过
                    # 会让「毕业态验证了参考答案」名不副实
                    print(f"  warning: solution 文件在作答区无对应文件，未覆盖：{solution_file.relative_to(overlay)}")
            # 里程碑特例：JAVA-MAPPING.md 的完成版也在 solution/ 下，毕业态同样覆盖
            # （结构检查与内容完成分开报告——见 test_mapping_meta.py 的完成度信号测试）。
            mapping_doc = overlay / "JAVA-MAPPING.md"
            if mapping_doc.is_file() and (dest / "JAVA-MAPPING.md").is_file():
                shutil.copy2(mapping_doc, dest / "JAVA-MAPPING.md")
        for cmd in (*THREE_COMMANDS, "ruff format --check ."):
            code, output = run(cmd, dest)
            print(f"  uv run {cmd:<24} -> {'PASS' if code == 0 else 'FAIL'}")
            if code != 0:
                tail = "\n".join(output.splitlines()[-12:])
                failures.append(f"毕业态 {cmd} 非绿：\n{tail}")

    # ---- 3. 结构校验（仅课时布局；里程碑无六段式讲义，不走 check_lesson） ----
    if (lesson / "exercises").is_dir():
        print("== 结构校验 check_lesson ==")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_lesson.py"), str(lesson)],
            capture_output=True,
            text=True,
        )
        print(result.stdout.strip())
        if result.returncode != 0:
            failures.append("check_lesson 未通过")
    else:
        print("== 结构校验 check_lesson ==")
        print("SKIP（里程碑布局，六段式结构校验不适用）")

    if failures:
        print("\n三态验证 FAIL：")
        for item in failures:
            print(f"  - {item}")
        return False
    print("\n三态验证 PASS")
    return True


def main() -> int:
    if sys.argv[1:]:
        lessons = [(ROOT / arg).resolve() for arg in sys.argv[1:]]
        missing = [str(lesson) for lesson in lessons if not lesson.is_dir()]
        if missing:
            print(f"目录不存在: {', '.join(missing)}")
            return 2
    else:
        lessons = sorted((ROOT / "units").glob("unit*/L*")) + sorted((ROOT / "units").glob("unit*/milestone"))
        if not lessons:
            print("未发现课时目录")
            return 1

    failed: list[Path] = []
    for lesson in lessons:
        try:
            ok = check_one(lesson)
        except (OSError, UnicodeDecodeError, shutil.Error) as exc:
            print(f"\n== {lesson.relative_to(ROOT)} 读取/镜像异常 ==")
            print(f"  {exc!r}")
            ok = False
        if not ok:
            failed.append(lesson)
    if failed:
        print(f"\n{len(failed)}/{len(lessons)} 个目录三态未过：")
        for lesson in failed:
            print(f"  - {lesson.relative_to(ROOT)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
