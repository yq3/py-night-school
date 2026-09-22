# Java 工程师第一次写 Python Agent，最容易被哪些「似是而非」概念坑到

> 发布渠道建议：掘金 / 知乎 / Java 技术公众号（分发计划见 [articles/README.md](./README.md)）。
> 素材同源：py-night-school Unit 1（L1.2 / L1.3 / L1.5 / L1.8），发布前如课程内容有更新，回读对应课核对。

你写了十年 Java，觉得 Python「一周就能上手」——上手是真的，事故也恰恰从这里开始。

真正的坑不是「不会」，而是「似是而非」：Python 的新概念长得都像你熟悉的老朋友，用 Java 的直觉去用它们，代码能跑、测试能过，然后在某个 production 下午突然不对劲。下面四个概念，是 Java 工程师转 Python Agent 开发时命中率最高的「直觉失效现场」——每一个都按「现象 / 最小复现 / Java 直觉为何失效 / 修复」拆开，你可以先猜猜自己会不会中招。

## 1. 装饰器像注解，但它是「替换」不是「贴标签」

**现象**：被装饰后 `f.__name__` 变成 `'wrapper'`、`f.__doc__` 变成 `None`。平时无感，一旦有别的东西**按名字或文档找函数**，当场爆炸——比如 Agent 框架的 `@tool` 装饰器，它靠 docstring 生成给模型看的工具描述。

最小复现：

```python
def deco_naive(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper  # 没有 @wraps


@deco_naive
def check_amount():
    """金额检查。"""


print(check_amount.__name__)  # wrapper
print(check_amount.__doc__)   # None
```

叠一层真实后果：把这个 `check_amount` 挂给 Agent 框架的 `@tool`，它第一行检查就是 `if f.__doc__ is None: raise ValueError`——你的坏装饰器让框架直接拒收。

**Java 直觉为何失效**：Java 注解是贴标签，**从不改变被注解元素本身**——`@Test` 过后方法还是那个方法，名字文档纹丝不动。Python 装饰器是替换：原名绑定的已经是 wrapper，元数据天然是 wrapper 的，除非你显式复制。

**修复**：装饰器永远 `@functools.wraps(func)`，贴在真正包住原函数的那层 `def` 上。已经丢了的现场可以用 `f.__wrapped__` 找回原身。

## 2. asyncio 像虚拟线程，但你睡的每一毫秒是「全场的」

**现象**：async 函数里一句 `time.sleep(0.3)`，全场所有任务被冻结 0.3 秒——并发消失、超时误报、心跳停止，且**没有任何报错指向肇事者**。

```python
async def fetch(claim_id: str) -> str:
    time.sleep(0.3)  # 毒药：不是 awaitable，也不让出
    return claim_id


# gather 里三个任务并发？不——全场串行陪它冻
```

**Java 直觉为何失效**：平台线程里 `Thread.sleep` 只挂起自己，完全合法；虚拟线程里它同样合法——JVM 会自动把载体线程让给别人。你的肌肉记忆是「sleep 是无害的礼貌行为」；asyncio 里只有一条线程，你睡的每一毫秒都是**全场的**。

**修复**：async 函数里只准 `asyncio.sleep`（把「等一下」翻译成 `await asyncio.sleep(秒)` 是肌肉记忆级别的迁移）；同步 IO 库与 CPU 重活不进 async 函数，需要时用 `asyncio.to_thread(func, ...)` 扔进线程池。排查手段：`asyncio.run(main(), debug=True)` 会报告卡住事件循环超过 100ms 的回调。

顺带一个孪生坑：调用了 async 函数但忘了 `await`——什么都没发生，功能静默失效，唯一线索是 `RuntimeWarning: coroutine ... was never awaited`。Java 里「调用」与「执行」是同一个动作，不存在「调了但没跑」的形态；pyright 的 `reportUnusedCoroutine` 能静态抓住这种裸调用。

## 3. 类型标注像类型系统，但运行时根本不读它

**现象**：签名明明写了 `int | None`，运行时传 `None` 照样炸——标注一个字都没拦。

```python
def late_fee_cents_bad(days_late: int | None) -> int:
    return days_late * 100  # 标注说了「可能 None」，但运行时它不拦


late_fee_cents_bad(3)     # 300，正常
late_fee_cents_bad(None)  # TypeError: unsupported operand type(s) for *
```

同一段代码交给 pyright，静态就抓到了：`error: Operator "*" not supported for "None"`——同一个错误，pyright 在你运行之前就报。

**Java 直觉为何失效**：Java 里你会写 `@Nullable Integer` + `Objects.requireNonNull`，或者 `Optional<Integer>`——IDE 和编译器持续盯着可空性；Python 的标注则只是「贴在函数上的数据」，解释器运行时根本不读它。防护为零，只有静态检查这一道防线——这道防线不跑就等于没有。

**修复**：联合类型入口先收窄——`if x is None: raise ...`，收窄之后才当 `int` 用；把 `uv run pyright` 当 `javac` 纳入每次提交（「跑类型检查」在 Python 世界不是可选项，是编译步骤的替代品）。

## 4. dataclass 字段默认值像字段初始化器，但它是「定义时求值一次」

**现象**：`ValueError: mutable default <class 'list'> for field items is not allowed`——注意，是**类定义时**抛，不是运行时踩雷。

```python
from dataclasses import dataclass


@dataclass
class Bad:
    items: list[int] = []  # ValueError 当场炸——dataclass 帮你挡了
```

**Java 直觉为何失效**：Java 的字段初始化器 `private List<Integer> items = new ArrayList<>();` 是**每次构造都执行的语句**，天然每实例一份。Python 的默认值不是语句，是**类定义时求值一次的对象**——之后所有实例共享同一个 list。Java 里「默认值 = 每次现做」，Python 里「默认值 = 定义时做好的那一个」，心智模型差在这一句。

**修复**：可变默认值一律 `field(default_factory=list)`——「工厂」= 每个实例构造时调一次 `list()` 现做。注意 dataclass 帮你挡了这一刀，但**普通函数的默认参数没有任何护栏**，同一颗雷换个地方埋（`def f(items=[])` 是经典面试题，也是经典生产事故）。

## 为什么值得把这些坑「命名化」

这四个坑的共同点是：**它们的错误形态都极其安静**——元数据丢了不报错、全场冻结不报错、`None` 穿透不报错、共享默认值不报错。等到炸的时候，现场离案发地已经隔了三层调用。迁移期最贵的不是「不会」，而是「似是而非」——这也是为什么值得给每个坑起名字（丢元数据 / 阻塞全场 / Optional 不设防 / 可变默认），团队里说一个词，所有人秒懂全程。

我在一套写给 Java 工程师的 Python Agent 开发课里（[py-night-school](https://github.com/yq3/py-night-school)），把这类陷阱全部按上面的四段式做了命名化拆解，而且练习是 pytest/ruff/pyright 三命令自动验收的——上面每个坑的「最小复现」，在课程里都是可以亲手踩一遍再修好的练习。30 讲里有 9 讲专门处理语言核心的迁移问题，然后才进 mini-agent 和框架。

**对应课程**（在线读，练习回仓库克隆跑）：

- 装饰器：[L1.5 装饰器 vs 注解](https://yq3.github.io/py-night-school/unit1/L1.5-decorators/)
- asyncio：[L1.8 asyncio ①](https://yq3.github.io/py-night-school/unit1/L1.8-asyncio-1/)、[L1.9 asyncio ②](https://yq3.github.io/py-night-school/unit1/L1.9-asyncio-2/)
- 类型标注：[L1.2 类型系统与 Protocol](https://yq3.github.io/py-night-school/unit1/L1.2-types-and-protocol/)
- dataclass / Pydantic：[L1.3 数据建模](https://yq3.github.io/py-night-school/unit1/L1.3-dataclass-pydantic/)

仓库：<https://github.com/yq3/py-night-school>（30 讲 · 练习即测试 · 主线无需模型 key，[五分钟跑通一个 Agent](https://github.com/yq3/py-night-school#先跑为敬五分钟零-key-跑通一个-agent)）。

如果这些 Java↔Python 对照和可验收练习对你有帮助，欢迎 Star 收藏——方便下次继续学，也让更多 Java 工程师能看到它。
