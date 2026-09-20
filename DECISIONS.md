# DECISIONS — 演进决策与复盘档案

> 宪法（[AGENTS.md](./AGENTS.md)）只保留规则层与一句话出处，本文件是它的叙事层：每条先例的完整来龙去脉、
> 各单元交付复盘、评审修复轮全记录。**改课 / 改共享件 / 改管线前，按宪法 §8 索引行的指针精读对应段。**
> 维护契约：规则或口径变更先改 AGENTS.md 规则层，完整叙事沉淀到本文件对应段；本文件内容**只增不减**
> （2026-09-20 自 AGENTS.md §4–§6/§8 迁出建档，信息零丢失——核验法：旧文句逐句可在宪法与本文件中检得）。

## 基础演进（定位 / 命名 / 学段 / Unit 1 / Unit 2）

个人学习计划 → 教程化；命名 `java2agent` →（歧义）→ `py-night-school`（机构隐喻可开新课、品牌伞）；Unit 1 补异常处理课（review 缺口）；「单元 = 学期」改「学段」；Unit 2 全单元交付 + 两轮复盘（对照组教学法落地：离线 mock 端点 + 剧本模型使零 key 可验收；锚定 mcp SDK 2.x——FastMCP 已改名 MCPServer，网上教程多为 1.x；2026 版 ruff 会 format Markdown 代码块，每课 pyproject `extend-exclude = ["*.md"]`）。

## 练习机制先例详档（宪法 §4 迁出）

- hints「形状」立规——先例：Unit 2 复盘，讲义 Step 已展示同构实现，hints 不自觉复述成代码，五课系统性泄底。
- 骨架 TODO 注释泄底（自查范围从 hints 扩大到骨架注释）：先例 Unit 3 复盘，L3.4 ex1 的 TODO 原样给出 `return [Send(...)...]` 列表推导、L3.3 ex2 给出 `Command(resume=decision)`，抄注释即过验收——泄底自查范围从 hints 扩大到骨架注释（hints 三级自查法对 TODO 注释同样适用）。
- 覆盖型 meta 单维缺口——先例：Unit 3 复盘，contract 只断言了 decision/部门维度，把某用例的 reason 改成与另一用例相同照样全绿（修法：reason 种类集单独一行 assert，五课同灌）。

## 工程纪律与流程先例详档（宪法 §5/§6 迁出，原句保全）

- **ruff line-length**：ruff `line-length = 120`（中文按双列宽计，100 太苛刻——实测结论）。
- **E501 出题**：出题陷阱先例：E501 要用**单字符串字面量**出题——`ruff format` 出于语义安全永不改写字符串内容（表达式拼接会被 format 自动拆掉，白教）。
- **JSON 夹具**：出题陷阱先例：JSON 测试夹具用 `json.dumps` 构造，不手写字符串——`'{"items": [4000] * 126}'` 是 Python 语法不是合法 JSON（Unit 2：夹具自己先红）。
- **量化口径**：**讲义量化结论必须可复现**：行数等统计写明工具与口径（如 ast 计数：定位各级 docstring 行区间后数非空非注释行），禁止依赖 shell grep 管道的隐式口径——先例：「292 行」因 BSD grep 不认 `\s` 而不可复现，四处复述全部返工为 249（ast 口径）。
- **外审环节**：提交外部 review——L0.1 先例：一轮 review 抓出 1 个参考答案 bug、2 个机制矛盾、1 个大纲缺口，此环节不可省；Unit 2 先例：一轮抓出 4 类系统性 P1。
- **修复轮语义回归**：L2.2 的「错误回喂」口径被错搬进 L2.1 的「跳过」口径，P0。
- **three_state_check**：自动镜像 data/ 共享素材、覆盖 solution、跑全部命令；先例：L2.x 全课用它验收。

## Unit 3 关键决策（先例与锚点）

①四框架同题 demo 的**共享件多课对版**（advice/mock_tools/review_rules/mock_endpoint 六课字节相同，test_contract 五课——L3.4 prebuilt 也带契约，展示「同题换装配」；改一处同步全部副本）；②新共享素材 `data/expense/review_mock.json`（expect_* 判分字段 + 覆盖型 meta），budget_mock.json 不动（Unit 2 兼容）；③框架依赖 == 钉到本地克隆 HEAD 对应版本，源码路标锚同一 commit（openai/openai-agents-python@fbd2dbca、langchain-ai/langgraph@e539ac122、langchain-ai/deepagents@9e7d62ff6、google/adk-python@7b246e01、langgenius/dify@79effdd498）；④L2.3 的 MockLLMEndpoint 全单元服役（框架模型客户端一律指向它，零 key 离线；adk 经 litellm 注意 `openai/` 前缀会被剥掉、传参用 api_base/api_key）；⑤openai-agents 第一件事 `set_tracing_disabled(True)`（trace 外发端点硬编码 api.openai.com，端点中立 ≠ trace 中立）；⑥L3.4 实测：Send 分支真并发（执行次序不保证）→ 批量剧本用「每单专属 mock 端点」；create_react_agent 在 prebuilt 1.1.0 已挂迁名 DeprecationWarning；⑦行数量化双口径并存：L3.8 决策表拆「装配 loc / 自写节点 loc」两列，milestone 工作台数「手写总行数」——列名不得再撞（先例：初版都叫「装配行数」学员无法自查）；⑧里程碑跨课重验（bench.py 子进程跑五课 contract）不得进 pytest——三态毕业态镜像不含兄弟课时，测试只用合成夹具，真跑是学员动作；⑨一轮外部 review 复盘（3 P1 + 择要 P2）：量化结论换 ast 实测口径（L3.4「约 40 loc」→20）、contract meta 补 reason 维度、adk web 目录约定以 cli 源码为准（每子目录一 agent.py）、骨架 TODO 注释泄底入 §4 新先例、计数与对版集合数逐处对齐（「共享件六课、契约五课」）。

## Unit 4/5 关键决策（先例与锚点）

①**外部产品课型定式「机制抽取件 + 加餐」**（L3.7 先例推广入 CURRICULUM）：主线＝把产品核心机制对版搬到报销域（锚产品 commit、零 key 三态可验收），真跑产品与本地分支改造是可选加餐——产品仓不进课时依赖、不内置上万行代码；②Unit 4 三课沿**风控嵌入位置光谱**递进（dimensions/A §3：L4.1 处置层③ / L4.2 决策层② / L4.3 授权+执行层④⑤），「宣称 vs 实现对码」进课当教学点（TradingAgents README「PM 审批」无代码）；③产品锚定 HEAD：virattt/ai-hedge-fund@fc1bf25（**v2 全量重写版，v1 的 src/agents/ 结构已不存在——网上旧教程全部失效，讲义明示**）、TauricResearch/TradingAgents@be952b8、HKUDS/Vibe-Trading@f84b2977；④L4.3 零运行时依赖（纯标准库贴合产品 frozen dataclass 哲学）；flock/msvcrt 平台差异不进学员代码、就地注释声明合理差异；⑤Unit 5 四课**对版生长**：L5.2/L5.3 是 L5.1 的并行分支、L5.4 汇合（非线性叠加）——共享件字节相同为默认、演进差异 docstring 就地声明；EVENT_TYPES 封闭词汇表跨课登记制（9→12：gate.checked/payment.executed/gate.denied，新事件类型登记并全副本同灌）；⑥**JAVA-MAPPING 诚实纪律**：Java API 名必须到本地克隆核实（langgraph4j@c2cf2e33、alibaba/spring-ai-alibaba@f82da0b50——**org 前缀是 alibaba，曾误写 spring-ai-alibaba/ 造成 12 处死链，2026-09-18 锚点复核修复**）、不存在老实写「需自建」——先例：外审抓出 getDiagram/ChatLanguageModel 两个编造名改真（getGraph(GraphRepresentation.Type) / ChatModel）；⑦L5.2 实测坑：httpx ASGITransport 读不了常开 SSE 流——`?mode=replay` 重放面是产品正当形态，live 顺序断言走生成器直测，坑如实写进讲义；⑧Unit 5 milestone 布局方案 A（unit2 先例）：编码 TODO 放根模块（solution/*.py 覆盖得到——**覆盖不递归进 tests/**），文档件（JAVA-MAPPING）用两态 meta（有占位 ⇒ 必须有 solution 对照版，零占位 ⇒ 直接过）；⑨外审升级为**全实证**（宪法 §4 自查法真执行：hints 抄进练习文件跑验收、锚点到克隆验文件存在、数量词 collect-only 实数）——四轮 P0×1（L5.1 ex3 hints L2 泄底，实锤「抄过即全绿」）+P1×9+P2×13 全修并重跑三态。

## 通读评审修复轮（2026-09-18，先例与锚点，评审档案见 [reviews/](./reviews/2026-09-18-readthrough-review.md)）

**课间叙事层入模板**——每课 h1 后固定承接段（昨晚产出→今晚新问题→排位理由，blockquote），单元页承担结构地图（unit1 前置列 / unit3 光谱图 / unit4 双线倒挂 / unit5 树形），check_lesson 校验承接段与结尾段存在；**写作契约机器化**——§2 开头全课对照表、三命令块单贴、练习表头「| 题 | 文件 | 考察 |」、Step 命名统一、发货态说明独立行、「Step N（可选）」加餐定式；**知识点登记制**（CURRICULUM §2.1）：唯一主讲课 + 复现课指路，先例：推导式曾 L1.1/L1.4 双主讲修为互指；**内部坐标纪律**：作者元引用（宪法 §x / 调研 dimensions / 第 N 次登场）不进讲义，A 编号配 unit5 速查表，外部产品首现须一句话身份；**锚点复核命令化**：120 条锚点 gh api 全验，4 类死链（org 前缀 / FastMCP 改名 mcpserver / 目录更名）修复并同灌 JAVA-MAPPING 三副本。教训：单课视角的质量流水线（check_lesson + 单课外审）抓不住跨课叙事问题，全单元交付后应加一轮通读评审。

## 新手友好度 + PyCharm + 双端命令 + 生态概念专项评审修复轮（2026-09-19，档案 [reviews/2026-09-19-novice-friendly-pycharm-review.md](./reviews/2026-09-19-novice-friendly-pycharm-review.md)，四审核点：单句级新手卡点 / IDE 触点 / Windows-macOS 双端 / 生态基础概念）

**IDE 侧栏定式**入 CURRICULUM §6 平台中立（blockquote `> **IDE 侧…**`、不入 bash 块、不作验收判据）——36 处插入 + L0.1 Step 7 扩容为双 checklist + 终端↔IDE 全量对照表（PyCharm 2025.1+ 原生 uv 为事实基线，Pro-only 能力标注）；**生态概念 101** 落 L0.1（虚拟环境/.venv、activate 为何从不需要、`uv run` 机制、pip↔uv 身世、ruff/Astral 身份、.python-version、wheel、[tool.*] 段）；**双端命令三缝隙先例**：仓库根脚本 `python3`→`uv run python`（unit5 里程碑重验五连）、`~` 家目录参数 Windows 不展开（unit3 README 克隆约定 + count_loc.py `expanduser()` 兜底）、加餐 export 补 PowerShell 对照块（L4.1）；P1 修复 L3.4 Step 3 补 clone+checkout。验证口径：check_lesson 30 课全 PASS + 改码三课（L3.4/L4.1/L4.3）three_state 全过 + handbook 44 页重建。

## 拆仓独立开源（2026-09-19，先例与锚点，收尾见 issue #1）

拆仓原则：教程在 lab 仓内保持自包含，research 档案不随仓发布。

自 lab 仓 `git subtree split` 拆出独立仓库（26 条历史 + MIT LICENSE）——**research 调研档案不随仓发布**，正文与元信息文档的相对死链（18 处，gh api 逐文件验证过存在）改锚 lab main 绝对 URL（`github.com/yq3/lab/blob/main/...`；锚 main 不锚 develop——develop 会漂移，main 走 PR 合并制不重写历史）；handbook 构建管线同步扩展：`rewrite_links` 对 lab 调研档案链接同样解包为纯文字——「research 不进站」的既有设计决定不因改绝对 URL 而破（效果分层：GitHub 讲义可点、站内保持纯文字）。

## handbook 在线阅读站

**在线阅读站提前落地**（§7 远期项 → handbook/ 原型：units/ 的 MD 仍是唯一事实源与机器校验对象、站点是纯构建产物不手写、转换只作用于 .stage 副本且 fence 外、落地页渐进披露/对照表着色/灯卡先在站内演示、课程 MD 逐课采用前先在 §3/§4 补组件语法约定；过程志与踩坑实录沉淀 handbook/README.md）；**handbook 公网上线**（2026-09-20 GitHub Pages `yq3.github.io/py-night-school`：push main → handbook-pages workflow `uv sync --frozen` + `uv run build.py` 直接发布构建 artifact，不建 gh-pages 分支、dist 不入库；build.py 注入 `site_url`，`HANDBOOK_SITE_URL` 环境变量可覆盖换域名；handbook/uv.lock 随仓提交钉死 CI 版本——README 已知限制挂的锁文件口径就此与课程纪律统一）。
