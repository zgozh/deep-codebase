# 维护者审查参考

本页只供维护者在独立审读之后核对，不放进作者或盲审上下文，Skill 运行时不读取。公开源码输入见 [cases](cases.md)；开发执行方法与实际状态见 [validation](../validation.md#v1115-开发试写方法与状态)。此处的预期事实不是打勾即可通过的答案表：事实正确与初学者能否仅凭正文复演分别判断，具体指出表达式和正文缺口，不按标签、字数或术语数量判分。

## 跨栈预期事实与常见漏项

### A：事件、异步恢复与 DOM

`index.html` 原行5–10构造表单、结果节点并加载模块；`app.js` 原行1–4获取元素引用和共享状态，6–8的 `render` 才把状态写成 DOM 文字。原行10注册的是函数，不在注册时执行其函数体；浏览器分派 submit 时才传事件，11阻止表单的默认提交。原行12先增加共享序号再保存当前调用的局部序号；13捕获这次输入并 trim，14–15先显示 Loading。17构造转义后的 query URL，await 恢复不等于阻塞浏览器，也不保证请求依发出顺序完成。

HTTP 503 本身不会使 fetch 的 Promise 拒绝；18–19显式抛错后进入24–26，当前请求显示 `Failed: HTTP 503`。成功需再 await JSON；22的比较发生在解析完成后。先发 `tea` 得序号1，再发 `milk` 得2，较迟完成的1在22或25提前返回，不能覆盖2，且不会执行28。它没有取消网络请求；两次处理共享 state、各有局部 request。正常给定 Tea 数据最终正文为 `Tea`。常漏：把 `data` 当 Promise、把 render 返回值当页面更新、只教成功不教 catch 也有过期保护、将 HTTP 状态误作网络异常、不给初学者讲引用/闭包/事件与两次暂停的区别。

### B：配置优先级与退出

`main.py` 原行25–26是直接运行入口，调用 main 后以返回的整数作为退出状态。6–9创建解析器、声明参数并真正解析；`--count` 未给为 None，给2经 argparse 的 int 转换为整数2。10–13仍先读取配置，即使给 CLI count 也不会跳过文件；`with` 离开关闭文件，默认路径按工作目录解释。14的条件表达式以 `is not None` 区分“没给”和零，CLI 优先于配置 count，但 word 仍来自配置；15转换最终值，16链式比较检查1至5。正常给2输出 `hello hello\n`，未给输出三次。给0在17抛 ValueError，19捕获再20调用 parser.error，向 stderr 输出用法/错误并以2退出，不到达21或22。文件缺失也经 OSError 进入同一路径；非法 `--count x` 则在9解析阶段退出，不进入此 try。

常漏：把 parser.error 当普通返回、把 main 的0和打印文字混为同一返回、说命令行覆盖便不用读文件、将 `None` 判断替成真值判断、漏讲配置读出的是字符串及 join/列表重复的具体结果。`config.get` 是 ConfigParser 方法，不是字典随意默认值；缺节/缺项属于 configparser.Error 的子类。源码读取可能有副作用边界，但没有配置写入。

### C：配置、注册与 HTTP 消费

`main.go` 原行12–19在服务启动前取环境字符串并转换；未设与空字符串同样落到默认10。`MAX_N=20` 得 max=20，oops 得转换错误，log.Fatal 结束进程，尚未注册或监听。20新建 mux，21把匿名函数注册为 handler，37才开始监听并由 HTTP 服务在请求到达时调用；注册本身不运行 handler。匿名函数捕获启动时 max，源码没有热更新。ResponseWriter 是写响应的接口，Request 指针提供请求；返回的是控制流，响应通过 w 消费，不是 return 一个字符串。

GET n=7：27 query 得字符串"7"，Atoi 给整数7及nil错误；28通过，32设置 Content-Type，33写 `14\n`。未显式 WriteHeader 时首次写默认状态200。n=bad或n=21在29写400及 `n out of range\n` 后30停止。POST先到22–25，写 Allow: GET、405、`GET required\n`，不解析n。写入正常响应失败只记录日志，不能撤销已经写出的响应。固定127.0.0.1是回环监听，样例不是完整生产安全方案。常漏：把两个 err 混成一个生命周期、漏 `:=` 声明范围或 `_` 丢弃计数、误称注册立即计算、遗漏短路判断/多返回值、说 http.Error 会自动 return、把 int 范围与业务范围混为一谈。

这些是当前有限案例的事实定位，不是其他技术栈的检查清单；真实试写仍需核全文教学与来源。三个案例通过也不等于任意规模/语言或长期学习效果已验证。

## 匿名候选提取方法

以下两稿故意保留已知缺陷，都是源码单元稿，不能以缺少其他九章为理由判它们失败。两稿各自含相同完整源码，源块无删行；路径 `/fictional/snapshot-demo/main.py`、原行1–21、Python3.11，学习者仅知变量与普通调用，尚未学对象方法、回调与容器副作用。第三份候选由维护者从 [校准的充分版本](../../deep-codebase-learning/references/teaching-calibration.md#写法三充分语义展开) 抽取正文并附同一完整源码，去掉“充分版本”、比较结论等身份提示，匿名混入；不让审读者加载标注版校准或本页。

维护者仅抽取下列各“候选正文开始”与“候选正文结束”之间内容，加上去身份的第三份对照，随机排列并重编号；向审读者另给上述同一学习者前置与单元范围，请先还原再核事实/教学。不提供答案key、已知缺陷或先前结论。编号无质量含义，抽取边界是普通文字，不是运行标记或新报告格式。

### 候选17

候选正文开始

本单元说明订阅快照怎样交到页面状态。Python3.11，完整虚构路径 `/fictional/snapshot-demo/main.py`，原行1–21：

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

`Snapshot("ready")` 产生保存 ready 和空列表的实例。调用 `snapshot.subscribe(render)` 时，实例自动绑定给 self，函数 render 绑定给 listener；传函数与调用函数不同，裸名字不执行 render。append 把函数存入列表，len 返回1给 token。回调是交给别人调用的函数，注册会把原行8的回调安排到订阅返回之后，所以原行21先打印 `1 None`，稍后 render 才把字典的 last 改成 ready。字典保存共享状态，render 没有返回值，状态才是其消费者要观察的结果。如果将原行7删掉，列表长度返回0，回调仍安排执行。这里没有取消订阅接口，token只是数量，不是可取消标识。

候选正文结束

### 候选42

候选正文开始

Python3.11，完整虚构路径 `/fictional/snapshot-demo/main.py`，原行1–21。本单元介绍保存快照、注册和消费：

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

原行1定义类，2–4初始化值和监听器列表。6–9实现订阅：7添加监听器，8立即调用，9返回数量。12创建状态，15–16定义更新状态的函数。19创建对象，20订阅，21打印。正常结果是 `1 ready`。原行8在返回之前调用 render，字典已更新，所以最后打印能看到 ready；token 是1。源码没有后续广播或取消功能，数量不等于取消标识。这样就把注册与消费连起来了。

候选正文结束

## 已知缺陷及结论边界

候选17事实错误：源码原行8是普通同步调用，没有任何安排稍后执行的设施，输出演算错误；两处“安排”及其时序均需修正。它还没有充分讲初始化、字典修改/隐式None、失败时部分注册保留等当前推导。候选42在现有陈述上事实正确，但用途/逐行动词和最终输出替代了教学：没有给初学者解释 self 与 listener 的绑定、实参求值、字典条目修改、append 与两条返回值的消费者，也没推导重要失败或修改后果。不能因为它写“立即”且结果正确就放行教学。

匿名充分对照只支持同一源码单元的可读判断，盲审者仍应给具体正文证据。实际这次 Luna Max 将匿名L37判为时序事实错/教学不足，L62判为事实对/教学不足，L08判为事实与教学在单元范围可试读；主会话核对后接受三类核心辨别，但不采纳L37“未说明self/listener绑定”的附加批评，因为候选确已提过。结果说明此次能辨别核心差异，也显示审读会误报，不能宣称盲审100%可靠；整课审读另覆盖十章与实际行为单元，不从候选测试升级真实教材状态。
