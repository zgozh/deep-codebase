# 源码单元教学校准

遇到“这只是概述”一类重大反馈，或难以区分准确概述与充分教学时，按需对照此页。平常写课不必加载。这里校准一个源码单元，不是十章整课、真实项目教材或规模标准；语言、行数、标题和篇幅都不是质量判据。

## 共用的完整源码

明确虚构的 Python 3.11 同步快照注册器。完整示例路径是 `/fictional/snapshot-demo/main.py`，下列块第一行为原行1，含空行共21行；定位采用该路径、符号和块内原行，不声称磁盘存在该文件。无第三方库、事件循环或后台任务。三种写法都解释这一份代码，包含直接调用者和状态消费者。

```python
class Snapshot:
    def __init__(self, value):
        self.value = value
        self.listeners = []

    def subscribe(self, listener):
        self.listeners.append(listener)
        listener(self.value)
        return len(self.listeners)


state = {"last": None}


def render(value):
    state["last"] = value


snapshot = Snapshot("ready")
token = snapshot.subscribe(render)
print(token, state["last"])
```

## 写法一：职责概述

`Snapshot` 保存当前值和监听器。`subscribe` 注册监听器、通知当前值并返回数量。`render` 更新状态，调用方打印结果。

这是准确的导航摘要。初学者仍不知道 `render` 与 `render()` 的区别、`self` 从何而来、通知发生在赋给 `token` 之前还是之后，不能据此独立推演当前代码。

## 写法二：伪逐行

原行1定义类；2定义初始化方法；3保存值；4创建列表。6定义订阅方法，7添加监听器，8调用监听器，9返回长度。12创建状态字典，15定义渲染方法，16更新状态。19创建快照，20订阅，21打印。

它覆盖了行号和动词，却仍让读者自己补求值、绑定、调用时点和消费关系。逐行格式本身没有增加这些含义。

## 写法三：充分语义展开

### 问题、位置和读前准备

本单元要回答：订阅者怎样在 `subscribe` 返回前就得到已有快照？初学者不必先懂事件系统。这里的“回调”是把函数交给另一个函数，由对方决定何时调用；这个例子决定立即调用。赋值把名字关联到一个值；圆括号表示实际调用，裸写 `render` 则取出函数对象。字典用键找到值，列表按顺序保存对象引用，修改容器会被持有同一容器的代码看到。`None` 表示尚无结果，不是文字 `"None"`。

类是创建具有数据和方法的对象的定义；`snapshot` 是其中一个对象。方法是关联于类的函数，`self` 是此处接收调用的那个对象。`def` 执行时创建函数而不执行函数体；缩进划定函数体。因此阅读先理解原行1–9、15–16的定义，真正的业务动作在原行19–21。以上完整源块就是本单元源码；路径 `/fictional/snapshot-demo/main.py`，原行1–21，核心符号 `Snapshot.subscribe`，入口原行19，消费者原行21。

### 原行1–4：先创建保存快照的对象

原行1的类体创建 `__init__` 和 `subscribe` 两个方法。原行19的 `Snapshot("ready")` 创建实例并调用它的初始化方法：新对象绑定给 `self`，字符串 `"ready"` 绑定给 `value`。原行3中等号右侧的 `value` 是参数；左侧 `self.value` 是该对象的属性，二者不能混成一个名字。原行4的 `[]` 新建空列表并保存到同一实例的 `listeners` 属性。构造完成后，这个对象关联到 `snapshot`，其 `value` 为 `"ready"`，`listeners` 为 `[]`。另建实例会执行另一次 `[]`，本源码没有把列表放成所有实例共用的类属性。

### 原行12、15–16：准备一个真实的消费者

原行12先创建字典并把它关联到模块级名字 `state`，键 `"last"` 的初值是 `None`。原行15的定义把函数对象关联到 `render`；此时不修改字典。实际调用 `render("ready")` 时，其参数 `value` 才得到 `"ready"`。原行16修改既有字典的一个条目，没有给名字 `state` 重新赋值，因此不需要 `global state`。`render` 没有显式 `return`，调用正常结束返回 `None`；它的有用结果是字典变化，原行21会读取这一变化。

### 原行6–9、20：注册内部就发生调用

原行20先求右侧 `snapshot.subscribe(render)`，完成后才给 `token` 赋值。取 `snapshot.subscribe` 得到绑定方法，调用时 Python 自动把 `snapshot` 作为 `self`，唯一显式实参 `render` 绑定给 `listener`。若写成 `render()`，会先调用 `render` 且缺少参数，尚未进入 `subscribe` 就报错；本源码传递的是函数对象。

原行7的 `self.listeners.append(listener)` 把同一个 `render` 函数对象放到实例列表中，列表成为 `[render]`。`append` 的返回值没有消费者；变化留在列表里。原行8取出实例属性的值 `"ready"`，随后执行 `listener("ready")`，也就是 `render("ready")`，于是 `state["last"]` 变成 `"ready"`。这次函数调用同步完成后才继续原行9；注册并不自动意味着等待未来事件，本代码也没有遍历列表或发送后续更新的操作。

原行9的 `len(self.listeners)` 此刻为整数 `1`，`return` 把它交回原行20，后者才完成 `token = 1`。变量名 `token` 不证明它是可取消订阅的标识：这里只返回当前数量，没有取消接口。原行8得到的 `None` 被忽略，与原行9返回的 `1` 是两条不同返回路径。

### 原行21、失败与修改判断

原行21先读取 `token` 的 `1` 和字典的 `"ready"`，再由 `print` 按默认空格分隔、末尾换行输出 `1 ready`。这是静态演算，未运行。它同时观察返回值和回调副作用，说明结果不是只靠 `subscribe` 的返回值传递。

当前 `render` 在给定输入下没有主动抛错。若以后传入的回调在原行8抛出异常，本源码没有 `try` 捕获：原行9不执行，原行20不完成赋值，原行21也不会到达，而原行7已经添加的引用不会自动撤销。这个推断来自实际顺序，不是声称当前正常例子已报错。若把原行7移到8之后，立即回调仍会发生，但异常时列表不再留下该引用；若删去8，新订阅者将不能立即得到已有值，状态会保持 `None`。是否需要回滚或延迟通知取决于业务契约，不能为模仿异步系统擅改当前设计。本单元只解释注册与首次消费，不教授不存在的更新广播、线程安全或取消功能。

### 规则来源与证明边界

这里把 Python 的规则用在具体实参和状态上：[Python 3.11 函数定义](https://docs.python.org/3.11/reference/compound_stmts.html#function-definitions) 区分定义与执行；[实例方法](https://docs.python.org/3.11/tutorial/classes.html#method-objects) 解释绑定对象；[列表操作](https://docs.python.org/3.11/tutorial/datastructures.html#more-on-lists) 说明 `append`；[赋值](https://docs.python.org/3.11/reference/simple_stmts.html#assignment-statements) 与 [return](https://docs.python.org/3.11/reference/simple_stmts.html#the-return-statement) 区分绑定、容器修改与返回。链接对应维护时实际读取的3.11文档，网页当前标记3.11.17；它们支持语言规则，不证明虚构程序运行或学习效果。

## 怎样使用这个差异

第三种写法提供了从未教概念到表达式、值、时机、消费者和后果的推导，读者可据正文复演，而不是靠审读者自己的经验补全。前两种可以作摘要，不能承担本单元教学。充分版本也只在这个单元范围内作示范；十章整课仍按原教学合同审读，不能把一个好单元推成全课通过。换语言或真实大项目时保留这种因果解释，源码规模与所需机制由当前职责决定。

教学迁移提示：表达式产出与消费动作也需要分开讲，例如 Python 的 `SystemExit(0)` 构造异常对象，`raise SystemExit(0)` 才抛出该对象；未被捕获的该异常使解释器以0退出，单写构造表达式不等于退出。依据为 [Python 3.11 SystemExit](https://docs.python.org/3.11/library/exceptions.html#SystemExit) 和 [raise](https://docs.python.org/3.11/reference/simple_stmts.html#the-raise-statement)；其他调用仍要读直接实现，不能由此推成“构造器没有副作用”。这是一种跨语言读法提示，不把该语法或本页示例语言当作 Skill 适用边界。

## 可选迁移对照：同一源码里的四种区别

下列仍用上面的虚构 `Snapshot`，只示范可迁移的解释形状，不新增项目主题、必备章节或深度上限；遇到对应疑点才读。

- **原段与可独立运行的改写**：若把原行6–9拆为6–7和8–9，首块末仍在 `subscribe` 内。边界可说“此时列表为 `[render]`，函数尚未返回，下一块仍在同一次调用内”；后块保留8–9的真实缩进。给首块另加 `return` 就改变了原实现，即使原行标签存在也不是保真摘录。
- **算出结果与教会模型**：`len` 算得 `1` 之前，正文已解释列表按顺序保存对象引用。原行7存入的是函数对象 `render`，不是执行结果 `None`；所以列表有一个元素，既能解释长度，也能解释为何原行8仍可调用这个对象。只写“注册数为1”没有教会这一差别。
- **角色箭头与真实接线/可达性**：不是只写“快照→监听器→状态”，而是由原行20把 `render` 绑定给 `listener`，原行8取 `self.value` 并调用它，原行16写字典，再由21读取。列表虽保存监听器，当前完整源码没有后续广播生产路径；不能从支持回调推成未来值会自动更新。
- **补齐与重复**：若读前准备已教裸写函数名与调用的区别，原行20正文应用到 `render` 和本次实参即可；返修应把缺少的绑定/时机解释放到该处，再去掉新增总述中逐字重讲的同一推导。保留前置模型、当前应用和局部回放各自职责，不靠压缩必要细节去重。
