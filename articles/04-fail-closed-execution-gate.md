# Agent 的 fail-closed 执行门：审批通过了，为什么还是不能付款

> 发布渠道建议：掘金 / 知乎 / 金融科技与企业自动化社群（分发计划见 [articles/README.md](./README.md)）。
> 素材同源：py-night-school L5.4 + Unit 5 里程碑；文中规则与裁决口径取自课程原文，发布前回读对应课核对。

做过企业系统的人都懂一句话：**「批准」和「执行」是两件事**。审批流走完、公章盖了，付款还要过财务的复核口——这是用几十年事故换来的架构常识。

Agent 系统里，这句话突然变得很值钱：模型说了 `APPROVE`，甚至人类审批人也点了确认——钱就能动吗？

## 场景：一个会付款的报销 Agent

设想一个财务 agent：查明细、预审、交给人工审批、然后执行付款。前面所有环节都绿了，最后在**唯一的执行出口**上，装一道纯函数检查链：

```text
审批单二次校验（真批了吗？批的是这版合同吗？——content_hash 对得上吗）
  → 供应商黑名单
    → 单笔上限
      → 当日累计
        → 当日频次
```

固定顺序，**首查命中即停**。策略长这样（金额一律整数「分」，不碰浮点）：

```text
policy: 单笔≤200000 分, 日累计≤500000 分, 日次数≤3, 黑名单=['sketchy-mall'], clamp=关
```

## 三态裁决，不是「过 / 不过」

这道门的输出不是布尔值，是三种一等裁决：

| 裁决 | 触发 | 有没有「修复」通道 |
|---|---|---|
| **DENY** | 结构性违规：不可解析 / 审批缺位 / 非 CONFIRMED / 指纹不符 / 黑名单 / 账本不可读 | 没有——不修改合同就永远不可能放行，而 agent 永远改不了合同 |
| **PAUSE_FOR_REAUTH** 或 clamp | 定量超限：单笔 / 日累计 / 当日频次超了 | 可以重新授权；或按策略裁到限额后放行（clamp 只缩不放，频次不可裁） |
| **ALLOW** | 全查通过 | 连「通过」也是带原因码的一等裁决，可审计 |

顺序本身就是设计：**结构性先于定量**。一笔单既进了黑名单又超了单笔上限，裁决停在黑名单——改数字救不了黑名单，先把「没救的事」说清楚。

## fail-closed 的魂：读不了账本，答案不是崩，是拒绝

这是整道门最能区分「写过 demo」和「上过生产」的一条：任何 `None` / 畸形输入的答案是 **DENY，不是 TypeError**。

课程里有一幕专门演示这个：当日已付清单里混进一条脏数据（缺金额字段的账本条目），门的反应不是抛异常让整单挂掉，而是——

```text
幕5 DENY  | 已付清单脏数据（fail-closed——宁可整单拒绝，不带脏账放行）
  -> DENY             reason=ledger_unreadable
     detail: today's ledger entry unparseable: {'vendor': 'airline-co', 'dept': 'SALES', 'category': '差旅'}（fail-closed）
```

宁可整单拒绝，不带脏账放行。与之配套的还有一条工程纪律：门的全部输入都必须是**显式契约**（不可变的 frozen 合同对象），「现在几点」这类环境信息不许在门内读时钟——否则同一个 (policy, intent) 在不同时刻给出不同裁决，审计就死了。

## 为什么 Java 工程师会对这套东西会心一笑

拆开看，这些全是你在 Java 侧做了很多年的事：

- **审批与执行分离**——工作流引擎里的 UserTask 与服务任务，模型输出只是「建议」，执行权在带检查的出口；
- **不可变合同**——sealed interface + record 的 Python 对应物 `@dataclass(frozen=True)`，错了就崩，不给「帮坏输入修复」的解析空间；
- **幂等与事件溯源**——恢复时同一节点从头重执行、执行史 append-only 落账、模型决策可回放原话；
- **限流与配额**——单笔 / 日累计 / 日频次三档限额，就是风控系统里的老三样。

区别只在执行容器：图执行器 + 纯函数检查链，替代了常驻引擎 + 规则服务。这个毕业设计最后产出的一张 [Python↔Java 架构映射表](https://github.com/yq3/py-night-school/blob/main/units/unit5-capstone/milestone/JAVA-MAPPING.md)，把十几个这样的模式逐行对译——每个 Python 物在 Java 栈的对应物、以及翻译时的坑（克隆里核实过才写，没有的老实标「需自建」）。

端到端跑起来是三条主链路（都有 pytest 集成测试盯着）：① 审批暂停 → 恢复 → 门 ALLOW → `payment.executed`；② 拒绝回环 → 新审批单（content_hash 变了）→ 批准 → 过门；③ 紧合同超限 → 门不付款 → `gate.denied` + 升级终态。全程无需模型 key——离线剧本模型就能把三条链路验收完。

**「批准只是授权，实际执行仍要过门」**——这句话值得贴在每个会动钱的 agent 系统的出口上。

这套东西来自 [py-night-school](https://github.com/yq3/py-night-school)——写给 Java 工程师的 Python Agent 开发晚课（30 讲，练习 pytest/ruff/pyright 三命令自动验收，主线无需模型 key）。本文对应的课：

- 执行门全课（检查链 + 三态裁决 + 结业自查）：[在线读](https://yq3.github.io/py-night-school/unit5/L5.4-execution-gate/) · [仓库源码](https://github.com/yq3/py-night-school/tree/main/units/unit5-capstone/L5.4-execution-gate)
- 毕业设计里程碑（四层合体 PoC + 集成测试）：[在线读](https://yq3.github.io/py-night-school/unit5/milestone/)
- 想先跑为敬：[五分钟零 key 跑通 ReAct 循环](https://github.com/yq3/py-night-school#先跑为敬五分钟零-key-跑通一个-agent)

如果这篇拆解和可验收练习对你有帮助，欢迎 Star 收藏——方便下次继续学，也让更多做企业系统的工程师能看到它。
