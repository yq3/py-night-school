# AGENTS.md — py-night-school 工作规范

> 本文档是教程项目的「宪法」：中心思想、课程设计理念与硬性纪律。**写课 / 改课 / 审课前必读**。
> 课表与课时明细见 [CURRICULUM.md](./CURRICULUM.md)；对外叙事见 [README.md](./README.md)；设计理念的方法论证据链见 lab 仓 [research/agent-tutorials/](https://github.com/yq3/lab/tree/main/research/agent-tutorials/)（landscape + report + profiles ×8）；演进决策与复盘全档案见 [DECISIONS.md](./DECISIONS.md)（本文件只留规则与索引）。

## 1. 中心思想

- **一句话**：写给 Java 工程师的 Python Agent 开发晚课——以 agent 开发为场景学 Python，以 Java 心智模型为桥。
- **双目的**：学员既获得 Python 工程能力，也获得可带回 Java 栈的迁移地图（毕业设计产出 JAVA-MAPPING.md）。
- **受众红线**：只服务「Java 熟、Python 略懂」人群。Python 已熟练者、零基础者、想学 LLM 原理者——在 README「招生对象」明确指路别处，不为他们加课。
- **空档定位**（不摇摆）：市场上无人占据的交集 = Java 桥 × 练习自动验收 × 源码深度 × 金融毕业设计 × 端点中立。证据：lab 仓 research/agent-tutorials/report.md（八仓解剖：练习验收是全行业空白）。

## 2. 课程设计理念（六特色，README 为准，此处为索引）

1. **Java 心智桥**——概念先给对照表；陷阱按「现象 / 最小复现 / Java 直觉为何失效 / 修复」四段命名化拆解；
2. **练习即测试**——TODO + pytest 自动验收，全绿即过关；
3. **对照组教学法**——Unit 2 手写 mini-agent 是全程对照组，OpenAI cookbook `Orchestrating_agents.ipynb` 是对照原件；
4. **源码路标**——`仓库@commit#路径`，读生产框架不读玩具；
5. **双贯穿线 + 金融毕业设计**——明线「报销单审查」从 L0.1 种下；暗线每课结尾「离毕业又近的一块」；
6. **夜校工程纪律**——竞品的系统性短板在这里默认不发生（见 §5）。

## 3. 课时模板：六段式（唯一结构，机器校验）

```
> 承接段（2–3 句 blockquote：昨晚产出 → 今晚新问题 → 为何排在今晚；单元首课回收上一学段）
## 1. 本课目标        （一句话、可验证；完成判据三命令块全课只贴这一次）
## 2. 概念讲解        （开头先给全课 Java↔Python 对照表，再逐小节展开）
## 3. 动手代码        （Step 化，code/ 目录支撑；小节统一「Step N」，可选标「（可选）」）
## 4. 练习            （单变量编辑约束 + hints 渐进披露 + pytest 验收；验收处一句话引用 §1 判据，不复贴）
## 5. Java 直觉陷阱   （命名化失败模式，四段式）
## 6. 延伸            （官方文档 + 源码路标 仓库@commit#路径；「与 mini-agent 对照」排在 §6 开头）
+ 结尾固定段「离毕业又近的一块」（暗线进度，散文体，下集预告写在这里）
```

写作契约（与 CURRICULUM §2 一致，check_lesson 机器校验）：术语首现即定义或标注「先混个眼熟，Lx.y 主讲」；练习表头统一「| 题 | 文件 | 考察 |」；完成判据口径统一「三命令全绿」。

话术约定：单元 = 学段、课时 = 晚课讲次、Unit 5 = 结业考；README 三个区块名固定为「招生对象 / 课表 / 入学指南」。

## 4. 练习机制（验收即毕业）

- **单变量编辑约束**：练习文件首行注释声明只改 TODO 区；验收测试文件头部注明「不要改本文件」。
- **hints 三级渐进**：第 1 级只给方向、第 2 级给形状、第 3 级才是接近完整的做法——答案只在最后一级（先例教训：初版第 1 级泄底被 review 打回）。「形状」= 伪代码/签名/提问式，**不含成行可抄的答案代码**（Unit 2 五课系统性泄底先例，详档：DECISIONS › 练习机制先例）。自查法：把第 2 级抄进练习文件，能直接过验收即为泄底。**TODO 注释同理**——骨架 TODO 只写「问什么/形状」，不写「返回什么」（Unit 3 抄注释即过验收先例，详档：DECISIONS › 练习机制先例；hints 三级自查法对 TODO 注释同样适用）。
- **三方对齐**：题目 docstring、hints、pytest 断言同一口径——**数量词也要兑现**：写「四态 / N 个测试」前先数实际断言；删测试时同步删 docstring 承诺（先例：Unit 2 两处「预审四态」实为三态/两态）。
- **import 约束口径**：练习首行统一「只改 TODO 区**与所需的顶部 import**，其余不要动」。骨架只预置 given 部分用到的 import——学生填完才用到的 import 预置了也会被 lint 判未使用删掉（Unit 2「import 六连发」根因）；所需的 import 在 docstring 或 TODO 注释里点名。
- **覆盖型练习配 meta-test**：题目要求是对用例表的覆盖时，验收测试直接检查用例表本身（结果种类 / 边界 / 数量）——先例：L0.1 ex2，它抓到的第一个 bug 就在参考答案里；覆盖维度要逐维断言，不留单维缺口（Unit 3 contract 漏 reason 维度照样全绿的先例与五课同灌修法，详档：DECISIONS › 练习机制先例）。
- **开放设计题**不硬造判分，给行尾 golden answer 诚实降级。
- **验收三命令**：`uv run pytest`、`uv run ruff check .`、`uv run pyright` 同时全绿 = 课时毕业。

## 5. 硬性纪律（check_lesson.py + 评审双保障）

工程纪律（全部源自竞品实测短板，出处 report.md §3.5/§3.6）：

- 每课是独立 uv 项目，**uv.lock 必须提交**；ruff `line-length = 120`（中文按双列宽计）。
- **平台中立**：学员命令一律 `uv run ...`；多步命令分行走（**不用 `&&` 串联**，PowerShell 5.1 不支持；机器校验只查 bash 块内的 `&&`）；平台差异（安装脚本 / 环境变量 / cp-copy）以对照块标注；不默认 macOS。
- 源码路标与外链延伸一律**锚定 commit**；讲义图片本地化，不外链 CDN；仓库**克隆即学**，教学主体不外置。
- **模型端点中立**：`.env` 三变量（`OPENAI_BASE_URL` / `OPENAI_API_KEY` / `MODEL_NAME`），每课目录带 `.env.example`；不绑任何云厂。
- 依赖陷阱先例：pyright 的 Node 走 `nodejs-wheel-binaries`（随 PyPI 镜像），不依赖 nodejs.org 直连。
- 出题陷阱先例：E501 要用**单字符串字面量**出题——`ruff format` 永不改写字符串内容（机制详档：DECISIONS › 工程纪律与流程先例）。
- 出题陷阱先例：JSON 测试夹具用 `json.dumps` 构造，不手写字符串（反例详档：DECISIONS › 工程纪律与流程先例）。
- **`ruff check --fix` 禁止作用于练习骨架**：会把「学生填完才用」的 import 当 F401 删掉；练习区只跑 `ruff format` 与不带 `--fix` 的 `ruff check`（Unit 2 先例）。
- **讲义量化结论必须可复现**：行数等统计写明工具与口径（如 ast 计数），禁止依赖 shell grep 管道的隐式口径（先例与 ast 口径定义详档：DECISIONS › 工程纪律与流程先例）。
- **源码路标锚点要验证存在**：`commits?path=X&per_page=1` 取到的「最后触达」可能是删除/搬迁该文件的提交（先例：langgraph prebuilt 死链）；锚定后用 contents API 带 ref 复核文件真实存在，且格式带 org 前缀（`openai/openai-python@…`）。
- **共享模块对版纪律**：同一模块的多课副本修 bug 必须同灌全部副本（先例：model.py 空 tools 修补未回灌 L2.3）；复制到不同目录层级时核对 `parents[N]` 深度与 docstring 内路径（先例：milestone env 路径 bug、mcp_server 文档路径残留）；合理差异就地注释声明。
- **外部依赖离线化**：凡调用外部服务（模型端点/MCP/子进程），配协议级测试替身——mock 端点（≈ WireMock）与剧本模型，使验收离线确定、无需 key；真实端点做 `--real` 可选加餐（先例：Unit 2 全单元零 key 三态可验收）。
- 业务约定：金额一律整数「分」；返回码 `REJECT:<原因>` 枚举风格；明线素材唯一来源 `data/`。

**三态验证法**（涉及代码的改动必须实测）：

1. **发货态**「精确红」：只有设计内的失败（TODO 未填的 failed、meta 未过的 failed、ex3 类设计内 ruff 违规），讲义示例部分必须绿；
2. **毕业态**全绿：solution 覆盖进 /tmp 副本后，三命令 + `ruff format --check` 全部通过；
3. `scripts/check_lesson.py` PASS。

三态可用一条命令跑：`python3 scripts/three_state_check.py units/<unit>/<lesson>`（自动镜像 data/ 共享素材、覆盖 solution、跑全部命令）。

## 6. 写一课的标准流程

1. 在 CURRICULUM 找课时定位（不做大纲外加课）；
2. 以 L0.1 目录结构为骨架复制（课时目录即独立 uv 项目）；
3. 写六段讲义 + code/ + exercises/（含 hints.py、meta-test）+ solution/；
4. `uv lock` 后 `uv sync`；
5. 跑三态验证（§5）；
6. 更新 README 路线图 checklist；
7. 提交外部 review——此环节不可省（两轮先例详档：DECISIONS › 工程纪律与流程先例）。
8. 复盘修复轮的纪律（Unit 2 先例）：任何改动落地后**全量重跑三态**——改了验收相关文件而未重跑 = 证据链失效；**修 hints 前先读该题三方**（docstring/测试/solution）——修复本身也会引入语义回归（P0 先例详档：DECISIONS › 工程纪律与流程先例）。三态已自动化为 `scripts/three_state_check.py`（支持课时与里程碑两种布局）。

## 7. 明确不做（防失焦）

- 不自研教学框架（hello-agents 第七章路线，直接指路）；
- 不写大部头理论（LLM/智能体史 → hello-agents 第一部分；MCP 深入 → mcp-for-beginners）；
- 远期才做：视频课 / 多语言 / 证书与榜单 / 在线阅读站 / 社区共创；
- 语言与领域红线：pandas 深入、Django、前端、可视化、ML 训练侧一概不进课表。

## 8. 文档地图与演进锚点

| 文档 | 角色 |
|---|---|
| [README.md](./README.md) | 对外入口：为什么 / 特色 / 课表 / 入学指南 / 路线图 |
| [CURRICULUM.md](./CURRICULUM.md) | 30 课时大纲 + 课时模板 + 练习机制 + 布局与纪律 |
| [DECISIONS.md](./DECISIONS.md) | 演进决策与复盘全档案——宪法先例的完整叙事层 |
| [reviews/](./reviews/) | 外部评审原始档案 |
| [research/agent-tutorials/](https://github.com/yq3/lab/tree/main/research/agent-tutorials/)（lab 仓） | 设计依据（创作输入，非发布物，未随仓发布；landscape 元数据级 + report 教学机制级 + profiles ×8） |
| `units/unit0-toolchain/L0.1-uv-toolchain/` | 六段式打样板（结构基准，以它为准复制） |

演进决策的完整叙事（各单元交付复盘、评审修复轮、拆仓、handbook 决策）**全部在 [DECISIONS.md](./DECISIONS.md)**——改课 / 改共享件 / 改管线前，按单元名或主题词检索对应段精读；本文件不留叙事，只留这一条指针。

## 9. 本机环境与提交约定备忘（作者侧事实与约定，与课程内容无关；2026-09-20 自 lab 仓 AGENTS.md 迁入并按当日实测修正）

- **除非用户明确要求，否则开发完成后不要提交到 GitHub**（不要 commit / push）。
- **Git 推送必须走 SSH**：remote 已配 `git@github.com:yq3/py-night-school.git`；本机 keychain 无 GitHub HTTPS 凭据，HTTPS push 会认证失败，勿改回 HTTPS。推送报错先 `ssh -T git@github.com` 排查（首次可能需 `ssh-add ~/.ssh/id_ed25519`）。
- **GitHub 访问备选序**：查仓库 / README / 文件内容优先 `gh api`（本机 gh 2.97.0 已登录 `yq3`，凭据在 keyring；安装于 `$HOME/install/gh_2.97.0_macOS_arm64/bin/gh`，**不在默认 shell PATH**——工具环境已注入可直接用，裸 shell 报 command not found 时用全路径，如 `gh api repos/{owner}/{repo}/contents/{path}?ref=<commit>`）。网络约束：`api.github.com` 稳定，`github.com` 网页与 raw.githubusercontent.com **间歇性超时**（lab 仓经验；2026-09-20 复测两者均 0.7s 可达——超时是波动不是永久墙）——**锚点复核一律走 `gh api`**，webfetch / curl 卡住时换 `gh api` 或 `git clone --depth 1 git@github.com:{owner}/{repo}` 到临时目录细读，不死磕。
