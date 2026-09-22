# 我用 250 行 Python 手写了一个可测试的 ReAct Agent，再逐个对照四个框架

> 发布渠道建议：掘金 / 知乎 / V2EX / LangGraph 中文社群（分发计划见 [articles/README.md](./README.md)）。
> 素材同源：py-night-school Unit 2 里程碑 + L3.8 对照总结课；文中数字口径见正文，发布前回读对应课核对。

学 Agent 框架最快的路，可能是先手写一个**没有框架**的。

不是玩具的那种「手写」——是完整走过一遍 HTTP + SSE 流式解析、工具注册与分发、ReAct 循环、结构化输出修复、MCP 桥接的五个模块，跑在同一道业务题上（报销单审查），然后每学一个框架，都回来问同一句话：

> **这层抽象替我付掉的是哪几行？收走的控制权是哪一个接缝？**

## 先看手写的这份：249 行，五个模块

```text
client.py       HTTP + SSE 流式解析
tools.py        Pydantic → JSON Schema → 注册表 → 分发
agent.py        ReAct 循环 + 双终止 + 执行器接缝
structured.py   解析 + 校验 + 失败回喂重试
mcp_bridge.py   MCP 工具桥接（子进程真协议）
```

行数口径说清楚（可复现，用 ast 定位 docstring 行区间后数非空非注释行）：核心五模块裸逻辑 **249 行**；含文档注释 454 行。一个下午能从头读完的体量——这就是「框架不神秘」的量化证明。

它能跑成什么样？下面是真实运行轨迹（离线剧本模型，不需要任何 API key）——查报销单 → 调预审工具 → 带原因拒绝，7 条消息消耗 3 轮：

```text
== ReAct agent 离线跑 ==
注册表: ['get_claim', 'preapprove']
user: 请审查报销单 CLM-2026-0003。

== 消息轨迹（7 条，消耗 3 轮） ==
     system: 你是财务预审助手。先用 get_claim 查单据明细，再用 preapprove 预审，最
       user: 请审查报销单 CLM-2026-0003。
  assistant: [选了工具: get_claim]
       tool: {"id": "CLM-2026-0003", "submitter": "赵工", "pu  (id=call_001)
  assistant: [选了工具: preapprove]
       tool: REJECT:INVALID_AMOUNT  (id=call_002)
  assistant: REJECT:INVALID_AMOUNT（报销单含负数金额明细，属脏数据）。
```

## 「可测试」不是形容词，是测试替身设计

Agent 最难测的部分是模型本身。这套 mini-agent 的做法是把不确定性拆开：

- **协议级 mock 端点**：一个 ≈ WireMock 的本地 HTTP 假端点，回放录好的 SSE 块（含跨块切断的坑）；
- **剧本模型**：按剧本出牌的模型客户端——想测「模型执念不收敛」，就给它一个永远选工具的剧本，断言第 4 轮恰好触发 `AgentBudgetExceeded`，一次不多；
- **真实工具、假模型**：工具（查单、预审）是真的，数据来自共享夹具——断言的是「工具真实被执行」，不是「打印出看起来正确的回答」。

于是验收可以离线、确定、零 key 地写下这些断言：结构化输出的修复循环里历史恰好五条、角色序列正确；MCP 桥接真的拉起 server 子进程走完整协议、未知工具抛 `McpToolError`；端到端 `CLM-2026-0002 → REJECT:ITEM_OVER_LIMIT` 与夹具的期望字段一致。这套测试哲学（接口隔离、测试替身、契约测试的 Python 版）对 Java 工程师来说应该非常眼熟——眼熟就对了，它是刻意搭的桥。

对照原件也诚实给出来：openai/openai-cookbook 的 `Orchestrating_agents.ipynb`（`run_full_turn` 循环）——写完 mini-agent 再去读它，你会认出每一个零件。

## 然后是对照：同一道题，四个框架重做

mini-agent 之后的八课，把同一道报销单审查交给 openai-agents、langgraph（手装图 + prebuilt 两课）、deepagents、adk 各做一遍，最后收成一张**能重新推导的决策表**（数字可用仓库里的生成器重跑复现）：

| 实现 | 依赖数（uv.lock 计数） | 装配 loc（ast） | 自写节点/循环 loc | 模型轮数（实测） |
|---|---|---|---|---|
| mini-agent（手写） | 44 | — | 249 | 3 |
| openai-agents | 51 | 15 | 0 | 2 |
| langgraph 手装图 | 54 | 10 | 20 | 2 |
| langgraph prebuilt | 54 | 6 | 0 | 2 |
| deepagents | 70 | 8 | 0 | 5 |
| adk-python | 88 | 9 | 0 | 2 |

这张表怎么读，比表本身重要：

- **行数和依赖数不是优劣排名**。它们回答的是「这层抽象替我付掉了什么」——mini-agent 那一行的「—」含义是「不交税，也不享受」；deepagents 的 70 个依赖买到的是子代理 + 文件系统 + 记忆三件套默认全给。跨层直接比数字，是选型评审最常见的翻车。
- 排序逻辑是**抽象光谱**：SDK → 图引擎 → harness → 全家桶，每往右一格，框架替你多管一层、你也多交出一层控制权。
- 每个定性结论要有机制证据。比如场景选型行（摘自课程决策表）：

| 场景特征 | 选 | 一句话依据 |
|---|---|---|
| 要断电恢复 / 审批外化 / 状态自持 | **langgraph** | interrupt + checkpoint 落盘、thread_id 隔离；显式图可审计；Java 生产栈（langgraph4j / spring-ai-alibaba）同源 |
| 一次性 POC / 要深度定制循环内脏 | **手写自研** | 249 行零锁定、messages 即公共协议 |
| 工作台型长任务（子代理+文件+记忆） | **deepagents** | harness 三件套默认全给——代价是收窄默认件、要覆盖它的预算默认值 |
| 已在 Google 栈 / 要调试器与 eval 工具链 | **adk** | adk web + AgentEvaluator 独一份——代价是 litellm 中转与生态绑定 |

## 为什么值得这么学一遍

框架课的常见学法是「跟着官方 quickstart 跑一遍」——跑完你只知道 API 长什么样，不知道它**替你做了什么决定**。先手写再对照的学法把这个顺序反过来：你带着自己写过的 249 行去看框架，每一段装配代码都能对上「这五行在我的 mini-agent 里是哪二十行」，控制权的交割看得见。

这套东西来自 [py-night-school](https://github.com/yq3/py-night-school)——写给 Java 工程师的 Python Agent 开发晚课（30 讲，练习 pytest/ruff/pyright 三命令自动验收，主线无需模型 key）。本文对应的课：

- 手写 mini-agent（任务书 + 十一路验收）：[在线读](https://yq3.github.io/py-night-school/unit2/milestone/) · [仓库源码](https://github.com/yq3/py-night-school/tree/main/units/unit2-mini-agent/milestone)
- 对照总结课（决策表生成器 + 跳读指南）：[在线读](https://yq3.github.io/py-night-school/unit3/L3.8-comparison/)
- 想先跑为敬：[五分钟零 key 跑通 ReAct 循环](https://github.com/yq3/py-night-school#先跑为敬五分钟零-key-跑通一个-agent)

如果这个「先手写、再对照」的学法和可验收练习对你有帮助，欢迎 Star 收藏——方便下次继续学，也让更多 Java 工程师能看到它。
