# LangGraph checkpoint：为什么杀掉进程后，Agent 还能恢复

> 发布渠道建议：掘金 / 知乎 / LangGraph·Agent 应用架构社群（分发计划见 [articles/README.md](./README.md)）。
> 素材同源：py-night-school L3.3（langgraph ②）；文中输出为课程真实运行日志，发布前回读对应课核对。

Java 工程师对「等一个人再继续」这件事有一整套肌肉记忆：Flowable / Camunda 的 UserTask，背后是一个**常驻引擎**在数据库和内存之间替你管理等待状态。所以第一次听说「langgraph 杀掉进程后还能恢复执行」，直觉反应通常是：它是不是也挂了个常驻的东西？

不是。它的答案朴素得多：**一个 sqlite 文件**。

## 机制就两件东西：checkpointer + interrupt

**checkpointer 把图的状态外置。** `compile(checkpointer=...)` 之后的执行模型变成：

```text
每个 superstep 结束：checkpointer.put(整份状态快照 + metadata{source, step})
每次 invoke 开始  ：checkpointer.get_tuple(thread_id) —— 有旧状态就续着跑
```

`thread_id` 像会话 id，但生命周期语义完全不同：Java 的 HttpSession 有超时驱逐、属于某个用户上下文；thread_id 只是一把**取货钥匙**——不过期、不属于任何人、谁拿到谁能读。记忆的形状也不是「会话 bean」，而是**消息史**：第二段对话进来时，恢复的是整份 `messages` 列表接着长。

**interrupt 的真实语义，以源码为准，不是文档比喻。** 文档把 interrupt 说成「暂停等人」，源码给出的机制精确得多。人审门节点里这样写：

```python
decision = interrupt({"claim_id": advice.claim_id, "reason": advice.reason})
return {"human_decision": decision, ...}   # 第一次执行永远走不到这里
```

第一次执行到 `interrupt()` 时，它在节点内部 **raise `GraphInterrupt`**——但这个异常**从不冒到你的调用栈**（它继承 `GraphBubbleUp`，源码 docstring 写明 "Never raised directly, or surfaced to the user"）：langgraph 的 pregel 引擎捕获它，连同图状态一起**落盘暂停**，`ainvoke` 正常返回。恢复时，另一个进程带着同一个 thread_id 重新 `invoke(Command(resume="approve"), config)`，引擎把人工决策经 scratchpad 送回 `interrupt()` 的**返回值**——注意，同一个节点**从头重执行**，这次 `interrupt()` 不再抛，而是拿到了人给的决定。

## 真分进程实验：这是全文的核心证据

课程里这个实验是真刀真枪分进程跑的——进程 1 把一张脏数据报销单打到人审门，然后**正常退出**（不需要 `kill -9`，Python 进程退干净就是等价的：内存里的图、模型连接、剧本队列全部消失）：

```text
[reviewer]
[tools]
[reviewer]
[__interrupt__]
模型请求: 2 次（剧本已耗尽，本进程退出后不复存在）
图暂停：next=('human_gate',)，step=3
interrupt payload: {'claim_id': 'CLM-2026-0003', 'reason': 'REJECT:INVALID_AMOUNT'}
thread_id: claim-CLM-2026-0003-234200
本进程即将退出——内存里的图、模型连接、剧本全部消失，存活的只有 db 里的 checkpoint。
```

然后是第二个进程（thread_id 抄上面打印的），approve 人工决策：

```text
== 进程 2（pid 44645）：approve claim-CLM-2026-0003-234200 ==
db: checkpoints/demo.sqlite3（与进程 1 是同一个文件，此外两进程无任何共享）
恢复前快照: next=('human_gate',)，interrupts=1 条
从 checkpoint 反推单据: CLM-2026-0003（REJECT:INVALID_AMOUNT）
模型请求: 1 次，发送 7 条消息——历史全部来自 db，剧本只供最后一轮台词
ReviewOutcome: APPROVE / PASS / 剩余 40000 分 / human=approve
events: ['reviewer', 'tools', 'reviewer', 'human_gate', 'reviewer', 'finalize']
```

两次 invoke 分属两个进程，状态一分不少地活过了进程死亡。发给模型的 7 条消息里，历史全部来自 db——这就是 HITL（human-in-the-loop）的机制底座。

## Java 人最容易摔的那一跤：给 interrupt 找 catch

看到 `interrupt()` 这个名字，Java 人的直觉会全部指错方向——`Thread.interrupt()` 设标志、`InterruptedException` 可捕获、catch 块就是处理点。于是两种典型翻车：

1. 在节点外面包 `try: ... except GraphInterrupt:`，或写 `finally` 清理「恢复点」——**永远捕不到**，`ainvoke` 压根不抛；
2. 以为图暂停后进程还挂在内存里等（像 `Object.wait()` / `CountDownLatch.await()`），于是「恢复」写成「让原线程继续」——但原进程早就退出了，你手里只有一个 sqlite 文件。

正确的 mental model：把 `interrupt()` 当**带外返回值**而不是异常。它下面的代码是「恢复重放路径」，必须**幂等**（恢复时同一节点会从头再执行一遍）；暂停信息用 `aget_state` 读（`snapshot.next` 与 `snapshot.interrupts`）；恢复入口统一 `invoke(Command(resume=...), config)` 且带同一个 thread_id——thread_id 丢了，暂停点就成了 db 里永远无人认领的一行。审计也别看日志栈，**看账本**：`get_state_history` + writes 表就是这条执行线的全部事实。

两张对照表收尾（Java 物 → langgraph 物）：

| 你熟悉的 Java 物 | langgraph 侧 | 关键差异 |
|---|---|---|
| HttpSession / Spring Session | checkpointer + `thread_id` | 存的不是会话 bean，是图执行状态快照——每 superstep 一份、可回放历史，没有超时与 TTL |
| Flowable / Camunda 的 UserTask | `interrupt()` + `Command(resume=)` | 暂停是「节点内抛-引擎捕-落盘」，恢复是**重新 invoke**——没有常驻引擎在内存里等你 |

这套东西来自 [py-night-school](https://github.com/yq3/py-night-school)——写给 Java 工程师的 Python Agent 开发晚课（30 讲，练习 pytest/ruff/pyright 三命令自动验收，主线无需模型 key）。本文对应的课：

- checkpoint 与 interrupt 全课（含分进程实验与练习）：[在线读](https://yq3.github.io/py-night-school/unit3/L3.3-langgraph-checkpoint/) · [仓库源码](https://github.com/yq3/py-night-school/tree/main/units/unit3-frameworks/L3.3-langgraph-checkpoint)
- 这个机制的毕业设计去向（审批外化 REST + SSE）：[L5.2 在线读](https://yq3.github.io/py-night-school/unit5/L5.2-approval-api/)
- 想先跑为敬：[五分钟零 key 跑通 ReAct 循环](https://github.com/yq3/py-night-school#先跑为敬五分钟零-key-跑通一个-agent)

如果这篇拆解和可验收练习对你有帮助，欢迎 Star 收藏——方便下次继续学，也让更多 Java 工程师能看到它。
