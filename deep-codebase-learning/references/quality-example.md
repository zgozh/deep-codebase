# 逐句成品形态与失败对照

供作者校准展开方式，判据仍以 [教学合同](teaching.md#唯一教学交付合同) 为准。前两个 Python 成品片段来自本 Skill 仓库公开维护脚本；后两个 JavaScript/React 例子是虚构教学示意，不是目标项目源码、运行记录或真实学习者证据。静态示例未运行，不自称 validated。具体行号只属于本次实际读取的工作树，使用时重新核对版本，不能照搬到别的项目。

可复用的是面向读者的视角、逐句说明语法与机制、贯通具体值和调用关系、标清证据边界的讲法；Python、Promise、React 只是这些例子选用的具体材料。写真实项目时按它实际使用的语言、框架和当前因果目标选择或改写讲法：项目没有前端就不引入 React，异步机制也按项目语言的实际语义解释；不要求每个项目都包含这些 API、界面、固定课程或标题。

## 成品片段：检查失败为何停止调用方

维护者检查发布文件时，需要“条件符合就继续，不符合就说明原因并停止”。条件是一个可判断真假的值；本例 `True` 表示符合要求、`False` 表示不符合。函数是一段有名称、可被调用的行为，参数是调用者交给它的值。`check` 不修复文件，只决定正常返回还是抛出错误。

返回是把执行结果交回调用方；`None` 是表示没有具体结果的特殊值，不是 `False`。调用栈是运行时保存“谁调用了谁、完成后回哪”的记录；本例错误先向 `check` 的调用者传播，再向更外层传播。

源段：`scripts/validate.py` 原行 21–23，符号 `check`，完整函数，无省略。真实调用者为 `validate`，例如原行 48 的文件软链接检查；上游交入检查结果和错误文字，函数不改变这些值；正常返回 `None`，调用方继续，失败抛 `ValueError`，调用方不再执行下一顺序步骤。此处只展开共同检查函数，文件枚举/软链接识别内部不计本例已教。

原源码摘录，行尾“教学”注释为本例添加：

```python
def check(condition, message):  # 教学：定义两个参数，定义时不执行函数体
    if not condition:          # 教学：不符合要求才进入缩进的下一行
        raise ValueError(message)  # 教学：把原因交给异常，离开正常返回路径
```

| 原行 | 语法、值与因果展开 |
|---|---|
| 21 | `def` 定义函数，`check` 是名称；括号内 `condition, message` 是按位置接收的两个参数，逗号分隔。冒号后的缩进表示函数体。执行定义只建立名称和函数的关联；调用 `check(False, "bad")` 时，才令本次 `condition=False`、`message="bad"` 并进入函数体，不会因看见定义就立即报错。 |
| 22 | `not` 对真/假取反，所以 `not False=True`。`if` 在其条件为真时执行下一级缩进语句；条件为假时跳过该块。本例失败值会进入 23 行，成功值 `True` 则使 `not condition=False`，跳过 23 行，走到函数体末尾。这里没有给变量赋新值，也没有改发布文件。 |
| 23 | `ValueError` 是 Python 内置的值错误类型，`ValueError(message)` 用原因文字构造异常对象；`raise` 抛出该对象，正常顺序执行中断。异常沿调用栈向调用者传播，直到遇到匹配的异常处理或结束该执行。本函数没有捕获，也没有正常返回值；调用方不会收到一个 `False` 再继续检查。 |

Python 语言参考的 [函数定义与 if](https://docs.python.org/3.15/reference/compound_stmts.html) 说明定义和条件块的规则，[raise](https://docs.python.org/3.15/reference/simple_stmts.html#the-raise-statement) 说明异常抛出与传播；本例按已读 Python 3.15 规则解释，没有据此声称目标项目或维护者运行环境已锁定 3.15。正常走到函数末尾返回 `None` 的规则见 [Python 教程](https://docs.python.org/3.15/tutorial/controlflow.html#defining-functions)。这支持上述语句语义，不能证明发布检查已经实际执行。

下面是另标的教学调用，不是源码原文，也不是项目已经运行的结果：

```python
check(True, "bad")
check(False, "bad")
```

第一行把 `True` 交给 `condition`，`"bad"` 交给 `message`；22 行判假，跳过抛错，函数隐式返回 `None`，调用者忽略该返回值后继续。第二行交入 `False`；22 行判真，23 行抛出文字为 `bad` 的 `ValueError`。假设外层没有捕获，第二次调用不正常返回，后续顺序语句不执行。两个调用都不修改任何文件；输出错误文字还是由宿主捕获后怎样展示，须读外层或实际观察，本例不能保证界面展示。

本课只解释“同一检查为何继续/停止”。后续可进入真实 `validate` 调用现场，把文件路径、谓词计算和错误文字串起来；不能从这个片段宣称已教完整发布流程。


## 成品片段：重复标题怎样成为不同锚点

维护者在文档写了两个 `## Setup`，链接 `#setup-1` 应能指到第二个标题。锚点是链接中 `#` 后用于定位文章内部位置的名字。这里的 `heading_ids` 只计算本脚本认可的名字集合，不执行浏览器跳转；Markdown（轻量文本标记格式）渲染器是否使用完全相同规则，还要核对目标平台，不能从本函数断言所有编辑器兼容。

源码依据：本仓库当前 `scripts/validate.py:31–39`，完整 `heading_ids` 函数，无省略。调用者是 `validate` 原行 71：把目标 Markdown 正文 `texts[destination]` 传入，拿返回的集合检查 `fragment` 是否在其中；不在则调用前例的 `check` 抛错。`texts` 是本次运行已读文件内容的字典，`destination` 是目标文件路径，`fragment` 是解析出的锚点；此处只展开标题名字计算，链接解析完整过程另讲。输入是假设正文 `## Setup\n## Setup`，不是实测日志。

原源码摘录，原语句无改写，行尾“教学”注释为本例添加；下面的正文按真实原行详细展开：

```python
def heading_ids(content):  # 教学：定义接收正文的函数，调用时才执行函数体
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)  # 教学：按每行模式提取标题文字列表
    ids, counts = set(), {}  # 教学：分别保存不重复锚点与基础名字已出现次数
    for heading in headings:  # 教学：依次处理每个标题，沿用本次调用的计数状态
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")  # 教学：转小写、删其余字符、去首尾空白并替换普通空格
        count = counts.get(slug, 0)  # 教学：取更新前次数，首次出现按0处理
        counts[slug] = count + 1  # 教学：写回增加后的次数，供后续同名标题使用
        ids.add(slug if count == 0 else f"{slug}-{count}")  # 教学：首次保留基础名字，再次按旧次数加后缀
    return ids  # 教学：全部标题处理后交回集合，不是每轮循环返回
```

原行31定义 `heading_ids`，参数 `content` 接收调用者传来的整篇字符串；此时不读取磁盘，也不调用网络。运行定义不执行函数体，进入调用后才从32行处理输入。

原行32的 `re` 是 Python 正则表达式模块，在本文件原行4导入；正则表达式是一种用模式选择文字的规则。`findall` 找到所有符合模式的内容并返回列表，供后续依次处理。`r` 前缀让字符串中的反斜杠保留给正则解析。模式逐项读：`^` 是行首，`#{1,6}` 要1到6个井号，`\s+` 要至少一个空白字符，`(.+)` 捕获一个或更多非换行字符作为标题文字，`$` 是行尾。`re.MULTILINE` 让行首/行尾作用于每一行；只有一个捕获组，所以得到的是标题文字列表而非带井号整行。本输入得到 `["Setup", "Setup"]`。本规则不是完整 Markdown 解析器，例如没有剔除代码围栏中的伪标题，不能教成全部标准行为。

原行33同时赋两个名字：`set()` 创建不重复元素的集合 `ids`，`{}` 创建键→值字典 `counts`。前者装最终可用名字，后者记每个基础名字出现过几次；它们是函数本次调用的内存对象，不是数据库，也不保存到下次运行。单有集合只能去重，无法告诉第二个标题该加哪个编号，因此这里同时需要计数。

原行34的 `for heading in headings` 从列表依次拿一个字符串放入 `heading`，缩进的35–38行每个标题执行一次。第一次和第二次都拿 `"Setup"`，但字典状态已经不同，所以结果不同；不是并行执行两个标题。

原行35先 `heading.lower()` 转小写得 `"setup"`。`re.sub` 把匹配的字符换成空字符串：方括号是字符集合，开头 `^` 在这里表示取反（与32行方括号外的行首不同）；`\w` 是字母/数字/下划线等单词字符，`\s` 是空白，`-` 在末尾为普通连字符。因此删除其余字符。随后 `.strip()` 去首尾空白，`.replace(" ", "-")` 把普通空格变成连字符。各步返回字符串，链式调用是把前一步结果交下一步，最后赋给 `slug`，不原地改 `heading`。两次本例均得 `"setup"`；如 `"Quick Start!"` 则得 `"quick-start"`，感叹号被删。

原行36 `counts.get(slug, 0)` 按键取已存次数，没有键就用默认值0，不报缺键错误。第一次字典为空，所以 `count=0`；原行37把 `count+1` 写回这个键，字典成为 `{"setup": 1}`。第二次36行读到1，37行写成2。局部 `count` 是更新前的次数，不能把37行的新值误当38行所用的值。

原行38在传给 `.add` 前先算条件表达式：`A if 条件 else B` 在条件为真时取A，否则取B，`==` 比较相等而非赋值。第一次 `count==0` 为真，取 `slug`；第二次为假，`f"{slug}-{count}"` 用花括号插入当前值，拼出 `"setup-1"`。集合 `.add` 将选中的字符串加入 `ids`，所以最终装 `setup` 和 `setup-1`。若省掉分支只加 `slug`，集合会把重复项合成一个，第二个标题的可用名字就丢了。

原行39的 `return ids` 在循环结束后交回集合并结束函数，不是每轮返回；缩进比35–38行浅说明它不在循环体内。调用方原行71用 `fragment in 返回集合` 做成员检查；正常假设 `fragment="setup-1"` 为真，`check` 正常结束，发布检查继续。失败假设 `fragment="setup-2"` 为假，`check` 抛出带目标信息的 `ValueError`；本函数不修链接，不会自动新增第三个标题。若无匹配标题，循环零次，返回空集合，同样交调用方判断。以上都是静态回放，未称真实执行成功。

已读 [Python 3.15 正则文档](https://docs.python.org/3.15/library/re.html) 的模式、findall/sub 与 MULTILINE 说明，以及 [字典 get/集合操作](https://docs.python.org/3.15/library/stdtypes.html)：前者支持32/35行匹配与替换的读法，后者支持36/38行默认取值和集合去重。规则在上述原行映射中消化；它们不证明本脚本实现完整 Markdown 语法，也不证明实际渲染。这里示范的是机制/值/Why/失败一起展开，不要求所有课套这一章法或复制这种表述长度。

## 成品示例：`async` 不会替内部 Promise 自动等待

下面的代码和推演值都是虚构的公开教学示意：它们不是目标项目源码、运行记录或学习者证据。`Promise` 与 `async` 是 JavaScript 例子的具体语义，真实项目要按所用语言解释对应的异步规则。这个例子只回答一件事：函数标了 `async`，是否就会自动等待函数体里调用的 Promise？

先把三个词落到具体值上。Promise（承诺对象）是 JavaScript 用来表示一项结果的对象：它可以仍在等待（pending），可以成功兑现并带一个值（fulfilled），也可以失败并带一个原因（rejected）。`await` 写在 Promise 前面时，会让当前 `async` 函数暂停这一步，等 Promise 成功后把兑现值作为表达式结果；若 Promise 拒绝，`await` 表达式会在当前函数中抛出其拒绝原因，之后的顺序语句停止执行，除非有异常处理。`async` 的规则不同：调用一个 `async` 函数总会得到 Promise，但它不会替函数体内每个 Promise 自动加上 `await`。

本例传给 `Promise.resolve` 的是普通空字符串 `""`，不是另一个 Promise，所以 `createSession()` 立即返回一个已经 fulfilled、兑现值为 `""` 的 Promise。它没有访问网络，也没有真正创建会话；空字符串不是会话编号。

```js
function createSession() { // 教学：定义普通函数；调用它才会执行函数体
  return Promise.resolve(""); // 教学：立即交回一个兑现值为空字符串的 Promise
}

async function send() { // 教学：定义异步函数；每次调用 send 都会得到 Promise
  createSession().catch(() => null); // 教学：给创建结果接一个拒绝处理器，但没有保存或等待新链
  return "sent"; // 教学：把 send 自己的最终值设为字符串 sent
}
```

`function createSession() { ... }` 是普通函数定义；花括号里的语句只有调用 `createSession()` 时才执行。调用时没有传参数，因此函数体无需形参。`return` 把表达式结果交回调用者，结束这次函数执行。这里表达式是 `Promise.resolve("")`：标准库方法接收空字符串，并立即给出已兑现的 Promise。这个教学函数既不发送请求，也不提供可用的会话 ID。

`async function send() { ... }` 定义了另一个函数。`async` 让 `send()` 的调用结果总是 Promise；它不意味着里面的 `createSession()` 自动被等待。函数第一句实际调用 `createSession()`，拿到兑现值为 `""` 的 Promise，再调用它的 `.catch(...)`。点号表示从这个 Promise 上调用 `catch` 方法；括号里的 `() => null` 是箭头函数，没有声明形参，因此不读取 `catch` 传来的拒绝原因；`=>` 后面的 `null` 是它被调用时返回的值。`catch` 只在前一条 Promise 链拒绝时调用这个函数。

`.catch(...)` 自己会返回一个新的 Promise，代表处理后的链。本例上游 Promise 已经 fulfilled，所以拒绝处理器不会运行；`.catch` 返回的新 Promise 最终也会以原来的空字符串兑现。代码没有把这条新链赋给变量、从 `send` 返回它，或对它使用 `await`，因此它的兑现值没有被本例后续代码读取。注意，`.catch` 仍然接上了对上游拒绝的处理；没有被消费的是 `catch` 返回的新链。

最后的 `return "sent"` 属于外层 `send`，与 `catch` 回调的返回值不是一回事。它结束 `send` 的函数体并把字符串交给 `async` 规则包装成 Promise。因此调用 `send()` 得到的是一个以 `"sent"` fulfilled 的 Promise；若调用方 `await send()`，拿到的最终值才是字符串 `"sent"`。内层的空字符串从未成为 ID，也不影响这个返回值。

把当前代码按实际值走一遍：调用 `send()` → `createSession()` 立即返回 Promise(`""`) → `.catch` 接上拒绝处理器但不调用它 → `.catch` 返回一条稍后以空字符串兑现的新链 → 这条链没有被继续读取 → `send` 返回值 `"sent"` → 调用 `send()` 的位置收到 Promise(`"sent"`)。因为示例使用已经 fulfilled 的普通值 Promise，不能据此说创建动作会晚于 `send` 完成；示例里甚至没有网络动作。它只证明 `send` 没有显式等待或使用创建结果。

如果将来把 `createSession` 改成可能拒绝的实现，才会进入假设分支：`() => null` 会运行并返回 `null`，于是 `.catch` 新建的链会以 `null` fulfilled。这个 `null` 只是错误处理链的结果，不是会话 ID；而 `send` 自己的 `return "sent"` 仍然决定它返回的 Promise 值。本例当前没有拒绝，因此不能把这段假设说成已经发生的失败处理。

MDN 的 [async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function) 章节说明每次调用 `async` 函数都会返回 Promise，函数可包含零个或多个 `await`；这对应 `send` 的异步返回规则，并不替缺失的 `await` 补出等待。MDN 的 [Promise.resolve](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/resolve) 章节说明普通非 Promise 值会让返回 Promise 立即 fulfilled；[Promise.catch](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/catch) 章节说明拒绝处理器在前序链拒绝时调用，`catch` 返回新 Promise。本例把这三条规则映射到 `""`、`() => null` 和 `"sent"`，只作静态语义推演；它不能证明任何真实会话创建或网络时序。

## 成品示例：父组件传入的值怎样决定 JSX

下面的组件、props 和界面结果也是虚构的教学示意：不是目标项目源码、浏览器运行记录或学习者证据。React 组件只是讲解界面条件的一种具体材料，真实项目没有前端或使用其他框架时不需要引入它。假设父组件要显示一条状态提示：只有 `thinking` 为真且 `isLoading` 为假时显示传入的文字；同时显示对应的状态标签。

JSX 是 JavaScript 的语法扩展，让代码可以写出类似 HTML 的标记。HTML（HyperText Markup Language，超文本标记语言）是网页常用的标记形式；这里 JSX 看起来像那些标签，但代码中的 JSX 是交给 React 的界面描述，不是 HTML 字符串。Props（properties 的简写，组件属性）是父组件通过子组件标签传给子组件的值；React 调用子组件函数时，会把这些值放在一个对象参数中。下面完整保留父组件调用、子组件定义、分支和所有 JSX 闭合符号：

```jsx
function NoticeExample() { // 教学：父组件函数，负责声明并传入本例的具体值
  return ( // 教学：把下面的子组件描述交给 React
    <StatusNotice
      thinking={true /* 教学：父组件传入布尔值 true */}
      isLoading={false /* 教学：父组件传入布尔值 false */}
      text={'正在整理答案' /* 教学：父组件传入这段字符串 */}
    />
  );
}

function StatusNotice({ thinking, isLoading, text }) { // 教学：React 用一个 props 对象调用此组件，参数解构出三个值
  const isThinking = thinking && !isLoading; // 教学：由两个布尔 props 算出本次渲染的判断值
  return ( // 教学：返回完整的 JSX 界面描述
    <section>
      {/* 教学：条件为真时才把文字段落放进界面描述 */}
      {isThinking && <p>{text}</p>}
      {/* 教学：保留条件成立与不成立时各自完整的标签 */}
      {isThinking ? (
        <strong>正在思考</strong>
      ) : (
        <strong>当前没有思考任务</strong>
      )}
    </section>
  );
}
```

先沿父子调用关系读。假设 React 正在处理 `<NoticeExample />`，它调用 `NoticeExample` 函数；父函数返回一个 `<StatusNotice ... />` 的 JSX 元素描述。`thinking`、`isLoading` 和 `text` 是这段调用现场的三个 props：具体值分别是布尔值 `true`、布尔值 `false` 和字符串 `正在整理答案`。React 接着处理这个子组件时，以包含这三个属性的对象调用 `StatusNotice`。组件不是由父代码直接写成 `StatusNotice(...)` 调用；React 在渲染组件时负责调用函数并读取它返回的描述。

`function StatusNotice({ thinking, isLoading, text })` 的参数是一个对象，并用 JavaScript 的对象解构把其中同名属性分别绑定到局部变量。于是这次调用中 `thinking === true`、`isLoading === false`、`text === "正在整理答案"`。`const` 声明一次赋值后不再重新绑定的局部变量；这句 `const isThinking = thinking && !isLoading` 先检查 `thinking`，为真才计算右侧 `!isLoading`。`!` 把布尔值取反，所以 `!false` 是 `true`；两个真值经 `&&` 得到 `true`，因此这次 `isThinking` 为 `true`。若改为 `isLoading={true}`，则 `!isLoading` 为 `false`，整个结果为 `false`。

`return (` 开始返回 JSX 描述。`<section>...</section>` 是完整的外层标签；`{...}` 在 JSX 标签内容中表示把大括号里的 JavaScript 表达式求值，并把结果放在界面描述中。第一处 `{isThinking && <p>{text}</p>}` 使用 `&&`：这里左侧确定是布尔值。当前 `isThinking` 为真，所以表达式结果是 `<p>` 元素描述，里面 `{text}` 取出父组件给的字符串，最终内容为“正在整理答案”。如果 `isThinking` 为假，表达式结果为 `false`，React 不显示一个写着 `false` 的文本，而是没有这个段落。

第二处 `{isThinking ? (...) : (...)}` 是条件（三元）表达式：`?` 后是条件为真时的结果，`:` 后是条件为假时的结果。当前值为真，所以 React 收到 `<strong>正在思考</strong>` 这一支；若值为假，则收到完整的 `<strong>当前没有思考任务</strong>` 这一支。真、假两侧都需要保留，括号帮助把多行 JSX 归在相应结果里。`</strong>`、`</section>`、`)` 和 `}` 分别关闭标签、返回表达式及条件表达式；它们共同构成可读且完整的 JSX 结构。

把本次具体值从头到尾代入，React 处理 `NoticeExample` → 父组件构造 `StatusNotice` 元素并传入 `true`、`false`、`正在整理答案` → React 以 props 对象调用 `StatusNotice` → `isThinking` 算为 `true` → `&&` 选中段落 → 三元表达式选中“正在思考” → React 消费返回的 JSX 描述。按这些规则演算，预期界面包含“正在整理答案”和“正在思考”。这是静态推演，不代表代码在浏览器中运行或已经观察到画面；示例也没有包含应用入口或挂载配置。

React 官方 [Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx) 章节把 JSX 说明为 JavaScript 内可写 HTML-like 标记的语法扩展；[Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component) 说明父组件把值传给子组件，组件通常从 props 对象中解构；[Conditional Rendering](https://react.dev/learn/conditional-rendering) 说明用 `&&` 和 `? :` 等 JavaScript 条件语法决定哪些 JSX 进入返回描述。本例分别映射到父标签的三个具体值、参数解构、局部布尔结果和两个完整分支。这些通用规则不能证明某个目标项目采用了哪一版 React，也不能证明真实浏览器画面。

## 这些写法必须退修

- “21行定义检查，22行判断条件，23行抛错误”：同义翻译，未解释 `def`/参数绑定/`not`/缩进/异常传播，仍未完成教学。
- “因为 `send` 是 `async`，所以它 await 了创建会话”：错误地把“调用总返回 Promise”说成“函数体自动等待内部 Promise”；本例实际调用 `send()` 得到兑现值为 `"sent"` 的 Promise，空字符串链没有进入 `send` 的返回值。
- 只贴 `createSession().catch(() => null)` 并说“失败时返回 null”：遗漏本例传入普通字符串的 `Promise.resolve("")` 已经 fulfilled，因此当前拒绝回调不会执行；也把回调的 `null` 错当成外层函数返回值或会话 ID。
- 只贴 `{isThinking && <p>{text}</p>}`，却没有给出 `isThinking` 的定义和父组件传值：读者无法知道条件来自哪里、当前真假如何计算，也无法复核最终显示内容。
- 只贴三元表达式真分支，删去 `:` 后的假分支，或裁掉 JSX 的关闭标签和括号：代码不再自足，不能说明条件为假时的完整结果，也无法确认返回结构闭合。
- 贴出 21–23 行后只说“检查失败会报错”：没有代码后逐句展开，即使行范围准确也失败；若把原文改成 `return False` 仍标该范围，也是错误源码。
- “点击按钮会调用 sendMessage，随后服务器收到 question”：若正文没写输入字段怎样交给状态对象、请求体/URL怎样形成及服务端取哪个参数，审核者不能自行补链，必须补正。
- “调用 sendEvent，所以页面先拿到编号”：静态调用可能遇关闭状态提前返回或网络未到达；未展示客户端接收/消费条件不能声称必然结果，末尾“未实测”不能抵消正文断言，必须补正。
- “检查通过：有源码链接、官方链接，作者已自查”：没有实际通读与必要解释，不能声称教材合格。

通读时只靠正文理解正常/失败过程，再核源码事实；自己懂 Python 或能查源码不表示文章已经解释。不需要把本例答案再抄成审查报告，具体缺口直接修正文。
