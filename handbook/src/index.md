---
title: Python 夜校
hide:
  - navigation
  - toc
---

<!-- 扉页：站内页面（不属于 units/ 课程源，不参与 check_lesson 校验）。文案取自仓库 README.md。 -->

<div class="ns-cover">
<h1 class="ns-title">Python Night School</h1>
<p class="ns-sub">Python 夜校——写给 Java 工程师的 Python Agent 开发晚课：以 agent 开发为场景学 Python，以 Java 心智模型为桥，一个学期从语言核心学到金融合规毕业设计。</p>
<p class="ns-meta">6 学段 · 30 讲 · 练习即测试 · 零 key 可验收 · 金融合规毕业设计</p>
<p class="ns-cta"><a class="ns-btn ns-btn--primary" href="unit0/">从 Unit 0 开始</a><a class="ns-btn" href="curriculum/">先看课表</a><a class="ns-btn" href="https://github.com/yq3/py-night-school">获取仓库</a></p>
</div>

## 先看 Agent 怎么跑（五分钟，零 key）

不用配置模型 API key，L2.3 的离线 demo 用剧本模型跑完整的 ReAct 工具循环：**查报销单 → 预审 → 带原因拒绝**。克隆仓库后，在该课目录执行 `uv run python code/demo_agent.py` 即可复现（实测输出节选）：

```text
     user: 请审查报销单 CLM-2026-0003。
assistant: [选了工具: get_claim]
     tool: {"id": "CLM-2026-0003", "submitter": "赵工", "pu  (id=call_001)
assistant: [选了工具: preapprove]
     tool: REJECT:INVALID_AMOUNT  (id=call_002)

 最终回答: REJECT:INVALID_AMOUNT（报销单含负数金额明细，属脏数据）。
```

它也是后续框架课反复对照的手写 mini-agent。

## 这门课的六个不一样

<div class="ns-feats">
<div class="ns-feat">
<h4>Java 心智桥</h4>
<p>概念先给「Java 对应物 + 关键差异」对照表再动手；每个陷阱按「现象 / 最小复现 / Java 直觉为何失效 / 修复」四段命名化拆解。</p>
</div>
<div class="ns-feat">
<h4>练习即测试</h4>
<p>每课练习是带 TODO 的代码，<code>pytest</code> / <code>ruff</code> / <code>pyright</code> 三命令全绿即过关。我们解剖的八个头部教程里，没有一个配套练习自动验收——这是我们的核心差异。</p>
</div>
<div class="ns-feat">
<h4>对照组教学</h4>
<p>Unit 2 先手写 ~250 行 mini-agent，之后每个框架课都回来对照「这层抽象替我付掉了什么」。</p>
</div>
<div class="ns-feat">
<h4>源码路标</h4>
<p>每课延伸给出 <code>仓库@commit#路径</code> 精确导读——学框架同时学读生产级 Python 源码。</p>
</div>
<div class="ns-feat">
<h4>双贯穿线</h4>
<p>明线「报销单审查」从第一课种下、四大框架同题重做；暗线财务 agent 毕业设计每课长一块。</p>
</div>
<div class="ns-feat">
<h4>夜校纪律</h4>
<p>中文原创、模型端点中立、每课独立 uv 项目锁定依赖、克隆即学——竞品实测暴露的系统性短板（版本漂移、外链失效、绑定云厂）逐项设防。</p>
</div>
</div>

## 练习在哪里

阅读站只负责「读」。这门课真正的主战场在仓库源码里——练习、提示、验收、参考答案都是以文件形态躺在课时目录中的机制，网页只能展示、带不走：

- **练习文件**：每课 `exercises/` 是带 TODO 的骨架，你来填空；
- **hints 三级渐进**：卡住时逐级展开提示，第 3 级才接近答案——纸面平铺会泄底，所以必须进文件；
- **自动验收**：每课是独立 uv 项目，`uv sync` 后 `pytest` / `ruff` / `pyright` 三命令全绿即本课毕业，不用等人对答案；
- **参考答案分离**：`solution/` 目录供对答案与复盘，验收测试文件头部注明不要改。

```bash
git clone https://github.com/yq3/py-night-school.git
cd py-night-school/units/unit0-toolchain/L0.1-uv-toolchain
uv sync
uv run pytest
```

克隆后跑通 L0.1 的验收，就算正式入学——之后的每一课都是这套节奏。

## 讲义在这里的读法

课程源文件是仓库里的 Markdown（单一事实源，机器校验的对象）；这个阅读站把它渲染成更适合晚上读的形态。下面三个组件对应教学机制的三个主张，讲义将逐课采用。

**对照即颜色**：Java 物与 Python 物在站内各有固定颜色（橙 / 蓝），对照表的列、代码块的语言顶边同套着色。

=== "Maven · pom.xml"

    ```xml
    <dependencies>
      <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <scope>test</scope>
      </dependency>
    </dependencies>
    ```

=== "uv · pyproject.toml"

    ```toml
    [dependency-groups]
    dev = ["pytest>=8", "ruff>=0.8", "pyright>=1.1"]
    ```

**渐进披露**：hints 三级提示在站内逐级折叠，按需展开：

??? note "第 1 级 · 方向"

    Python 的「块」由什么界定？花括号吗？——想想缩进层级决定代码归属。

??? tip "第 2 级 · 形状"

    缩进层级 == 块归属。检查出错那行的缩进与谁对齐：`def` 体？`if` 分支？

??? success "第 3 级 · 做法（接近完整的参考）"

    统一 4 空格一层，`def` 体整体缩进；提交前 `uv run ruff format .` 一键归一——但格式化器永远不会改写字符串内容。

**每课一格灯**：每讲结尾的「离毕业又近的一块」渲染成灯卡，进度拼图逐课点亮（演示：完成 L0.1 后的第一格）——

<div class="final-note">
<p class="ns-cells-label">1 / 30 讲</p>
<div class="ns-cells">
<i class="on"></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
</div>
<h2>离毕业又近的一块</h2>
<p><code>preapprove()</code> 就是毕业设计「fail-closed 执行门」里<strong>限额检查</strong>的雏形（纯函数、整数分、可参数化测试）。到 Unit 5 你会把它升级成检查链——今晚你已经写下了最后一环的种子。</p>
</div>

> 6 学段 30 讲已全部上线。课程内容以仓库 `units/` 的 Markdown 为唯一事实源；练习与验收请回到仓库完成。右上角可切换浅色 / 深色主题。
