# 成品教材与局部展开参照

本例是完整的十章公开教材，用来示范如何把真实代码、输入、值变化、调用现场和边界写成一篇可独立阅读的课。现行要求以[教学合同](teaching.md#唯一教学交付合同)为准；第五章在各源码单元里先交代业务问题和调用输入，再给出完整代码，最后按原行讲清执行过程；小节标题随代码职责变化，不重复套同一组问句。

下文代码来自公开仓库 `scripts/validate.py` 的固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`。代码块内标成“教学注释”的行尾注释是本文新增提示，其余 Python 语句保持该提交原样。示例目录、Markdown 内容和运行结果是静态教学假设，不是仓库文件、运行记录或浏览器观察。

## 完整示例课：从 Markdown 标题算出本地链接锚点

### 1. 业务场景与本课目标

维护者改完文档后，发布检查要发现失效的本地链接，避免文档指向一个并不存在的文件或标题。这里的发布检查是仓库在交付前运行的一组自动检查；它读取仓库文件并给出通过或失败结果。Markdown 是用普通文字和少量标记写文档的格式；下面的 `## Setup` 用两个井号表示二级标题。

本课只跟一条链接：源文档在 `ROOT/docs/start.md`，目标文档在同一目录的 `ROOT/docs/guide.md`，两份文件都已在本次检查读取的文件集合中。`ROOT` 是为教学假设的项目根目录；为让示例中的相对路径和错误消息稳定，下面统一用斜杠写路径，例如 `/work/project`，这不是仓库里的真实路径。源文档包含一个指向目标文档第二个 `Setup` 标题的链接：

```markdown
<!-- 假设文件：ROOT/docs/start.md -->
参阅[设置指南](guide.md#setup-1)。

<!-- 假设文件：ROOT/docs/guide.md -->
# Café, Tea!
## Setup
## Setup
## Setup
### API_v2
```

链接目标 `guide.md#setup-1` 由两部分组成：文件名 `guide.md` 和井号 `#` 后的片段 `setup-1`。片段是链接中用于指向文档内部位置的文本。源文档和目标文档同目录，所以这个相对文件名从 `docs` 目录解析到 `ROOT/docs/guide.md`。这里预期的结果是：检查器把标题转换成标识集合，找到 `setup-1`，然后继续检查；如果把链接改为不存在的 `setup-9`，检查器会报告错误并停止当前这次发布检查。

读完本课，你应能沿着这条具体路径解释：目标文字怎样被拆成路径和片段、目标文件怎样定位、标题怎样生成标识、重复标题怎样编号、谁检查成员关系，以及错误怎样影响调用方。本文不要求你先懂 Python、正则表达式、文件路径或 URL。

### 2. 系统位置与架构分工

#### 从脚本入口走到链接检查

`scripts/validate.py` 是发布前检查仓库文件的 Python 脚本，不负责网页导航。文件末尾只有在脚本被直接运行时才调用 `validate()`；后续章节只沿这次调用的一条本地链接往下走。[入口在固定提交原行 121–122](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L121-L122)。

#### `validate()` 为什么持有文件和文本

`validate()` 先确定要检查的文件集合 `files`，再把文件内容读进 `texts`。`UTF-8` 是 `8-bit Unicode Transformation Format`（八位 Unicode 转换格式）：它把 Unicode 文字编码为字节以便存入文件，再把读出的字节还原为文字。一个字节由 8 个比特（0 或 1）组成，一个字符可能需要多个字节；本脚本用 UTF-8 读取，才能把 `Café` 这样的内容还原成字符串。`Path` 是代表文件系统位置的对象，不是文件内容。`texts` 用路径对象作键、文本字符串作值，因而稍后可以用已解析出的目标路径取回目标内容。[固定提交原行 43–53](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L43-L53)。

每轮链接循环里，当前文件路径 `path`、当前正文 `content` 和给错误消息用的相对路径 `relative` 已由外层绑定；目标循环再把一个目标放到 `target`。这些不是标题转换函数的输入。`validate()` 持有它们，是因为它必须把链接文字、文件清单和已读内容连接起来：先定位目标文件，再取出该文件正文，最后检查片段。

#### `heading_ids()` 为什么只收正文

`heading_ids(content)` 只接收一段文本并返回标题标识集合。它不自己打开文件，也不接收来源路径或链接片段。这样标题规则和文件读取分开：调用方负责取得正确文本；标题函数只根据给定文字算结果。维护者若要检查一种标题文字怎样转换，可以把该文字单独交给这个函数推演；文件定位错误仍由调用者处理。这个边界让文本转换不依赖磁盘读写，便于独立核对输入和输出；这里说明的是由函数接口带来的能力，不声称仓库已有专门测试。[函数在固定提交原行 31–39](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L31-L39)。

#### `check()` 把条件交回调用链

在原行 69，`check` 接收“目标是否在发布文件集合里”的真假结果和文件错误消息；在原行 71，它接收“目标片段是否在标题集合里”的真假结果和锚点错误消息。条件为真时，`check` 不抛出异常，调用者可以走到下一条语句；条件为假时，它抛出带有调用者消息的 `ValueError`，这是 Python 内置的异常类型，本例用它表示链接没有通过检查。异常是打断正常语句顺序的错误信号，传播方式在第三章展开。这个函数不打印消息、不改文档，也不替调用者选择继续还是退出；异常沿 `validate()` 调用链传播，脚本入口没有在这条路径上捕获它。[检查函数原行 21–23](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L21-L23)；[调用现场原行 64–72](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L64-L72)。

#### 状态在什么时候存在

一次 `validate()` 运行时，`files` 和 `texts` 为这次检查提供文件清单与文本；目标循环依次处理各个 `target`，成功处理后才在原行 72 增加 `links`。每次 `heading_ids` 调用会重新建立自己的标题列表、计数字典和标识集合。`return ids` 把标识集合交回调用方，供这一次 `fragment in ids` 判断；标题列表和计数字典留在函数内部。它们都是内存中的本次调用状态，不会写回文件，也不会保存到下一次脚本运行。若锚点检查抛错，行 72 尚未执行；本次调用会退出，未交出的局部值随函数退出而不再供后续目标使用。

### 3. 读懂本课所需的概念

#### 函数先定义，再由调用提供输入

Python 文件是一串交给解释器按顺序执行的语句。函数是有名字、可重复调用的一组语句。`def heading_ids(content):` 建立这个函数，**但不会在定义时处理标题**；真正调用 `heading_ids(texts[destination])` 时，Python 才先取出括号里的正文，再开始执行函数体。`content` 是形参，也就是定义里接收输入的名字；`texts[destination]` 是实参，也就是这次调用实际交来的值。形参绑定到实参后，函数内部通过 `content` 读到那段正文。

作用域是一个名字可以被代码直接使用的范围。`content`、`headings`、`slug` 是这次 `heading_ids` 调用里的局部名字；函数外不能直接读它们。函数可以通过 `return` 把指定结果交出去，调用方再把结果存入自己的名字。缩进表示哪些语句属于函数、循环或条件分支；冒号开启一个缩进块。第 39 行的 `return ids` 位于循环之后，所以循环处理完才交回集合。

#### 导入模块，让当前文件能使用工具

`import re` 运行时会把 Python 标准库里的正则表达式模块绑定到当前文件可用的名字 `re`。模块是一组相关工具；`re.findall` 表示从 `re` 模块取出 `findall` 工具，点号把名字和模块里的工具连起来。标准库是 Python 随附的常用模块集合，不需要项目另写这段匹配逻辑。脚本也导入 `Path` 和 `unquote`（原行 7–8）：`Path` 创建路径对象，`unquote` 解码百分号编码。导入只让这些名字可用，不会自动调用标题函数。

#### 用字符串和正则模式寻找标题

字符串是程序中的一段文字，例如 `"## Setup"`。正则表达式是描述文字形状的模式，`re` 模块按这个模式扫描字符串。标题模式是 `r"^#{1,6}\s+(.+)$"`：`r` 让 Python 把反斜线原样交给正则规则；`^` 找字符串开头，启用 `MULTILINE` 后也找每一行开头；`#` 是字面井号，`{1,6}` 表示前面的井号重复一到六次；`\s+` 要求一个或多个空白；`(.+)` 用括号捕获至少一个字符，`.` 默认不跨换行，`+` 表示一次或多次；`$` 找字符串结尾或其最后换行之前，启用 `MULTILINE` 后也找各行结尾。`findall` 按顺序收集括号捕获的文字。

另一条模式 `r"[^\w\s-]"` 用于删除标题中的字符：方括号表示一个字符集合，开头的 `^` 表示“不属于集合”；`\w` 是字母、数字或下划线，`\s` 是空白，放在末尾的 `-` 表示字面连字符而不是范围。此处的 `^` 在方括号外表示行首，方括号内则表示排除；位置不同，含义也不同。`\s` 也匹配换行，因此一行只有 `#`、下一行写 `Next` 时，`\s+` 可能跨过换行并捕获 `Next`；这条规则只是在文本中找形状，不是完整的 Markdown 标题解析器。

模式里的 `\w` 在 Python 默认 Unicode 字符串模式下匹配字母、数字和下划线，`\s` 匹配空白。`MULTILINE` 让 `^` 和 `$` 分别把每一行当作边界；`DOTALL` 会让点号也能匹配换行，本例没有启用它。`ASCII` 是 American Standard Code for Information Interchange（美国信息交换标准代码），这里的 `a-zA-Z` 只接受 ASCII 英文字母；链接前缀检查故意不使用所有 Unicode 字母。`slug` 在本文指由标题文字算出的短标识，例如 `Setup` 会变成 `setup`；它不是 Markdown 各平台共同规定的名字。

#### 标题文字、Unicode 和容器各自保存什么

Unicode 是让不同语言文字用统一字符编号表示的标准。`Café` 中的 `é` 若存成一个预组字符，会被 `\w` 保留；也有人用字母 `e` 加一个单独的组合重音符表示相同外观。当前模式会删掉不属于 `\w` 的组合重音符，因此两种写法可能分别产生 `café` 与 `cafe`。代码没有把这两种编码形式先统一，这就是此处的规范化限制。字符串方法会产生新的字符串，不会在原字符串内部改字。

标题提取先得到列表 `headings`，例如 `['Café, Tea!', 'Setup', 'Setup', 'Setup', 'API_v2']`；列表能保留出现顺序，所以第二次 `Setup` 可被识别为第二次。字典 `counts` 把基础名字映射到出现次数，例如处理三个 `Setup` 后是 `{'setup': 3}`。集合 `ids` 保存最终可查的名字，例如 `{'setup', 'setup-1', 'setup-2'}`；它去重，不记录插入顺序。三种容器不能互相替代：列表给处理顺序，字典记次数，集合用于回答“是否存在”。`API_v2` 只是本课的一个普通标题字符串，计算结果为 `api_v2`；这里没有调用任何项目 API。

`counts.get(slug, 0)` 在键不存在时给默认值 0。`count = ...` 让局部名字指向读出的旧整数；后续 `counts[slug] = ...` 改字典，`ids.add(...)` 改集合。这是重新绑定一个名字与修改已有容器的区别。表达式是一段能算出值的代码：`count == 0` 得到真或假，`fragment in ids` 得到成员检查结果；这两种比较会返回布尔值 `True` 或 `False`，`bool` 是它们的类型名。`if` 和条件表达式也能接收其他类型的值，再按真假判断：非空字符串为真，空字符串为假，数字 `0` 和 `None` 也是假。因此原行 68 的 `if filename` 与原行 70 的 `if fragment` 检查字符串是否非空，并不要求它们本身是布尔值。

#### 路径、URL 与目标文字的三段拆分

`URL` 是 Uniform Resource Locator（统一资源定位符），完整的网址通常还会包含用来定位网络服务的前缀和主机位置。本课里的 `guide.md#setup-1` 没有网址前缀或主机，是从当前文档出发的相对链接目标；`#` 后的 `setup-1` 是目标文档片段。`https:` 是安全网页传输地址常见的 scheme（处理方式前缀），`mailto:` 是邮件地址常见的 scheme；代码只用冒号前的前缀识别并跳过这些目标，不访问它们。

`str.partition('#')` 在第一个井号处切开，并给出固定三项的有序元组：分隔前的文本、分隔符、分隔后的文本。元组是一组有顺序且数量固定的值，因此 `guide.md#setup-1` 得到 `('guide.md', '#', 'setup-1')`。左侧的 `filename, _, fragment` 同时接收这三项；`_` 在 Python 里仍是普通名字，这里表示分隔符接到后不再使用。若目标是 `#setup-1`，文件名前半段为空，表示当前文件中的片段。

`unquote` 把 `%20` 这类百分号后跟十六进制数字（`0`–`9`、`A`–`F`，小写 `a`–`f` 也可）的编码还原为文字；它不联网，也不会把 `+` 当成空格。`Path` 路径对象代表文件系统位置，与保存路径文字的字符串不同：`path.parent / filename` 把目标文件名接到源文档目录后，`.resolve()` 得到绝对规范路径并处理 `.`、`..` 等路径部分，`.suffix` 读取后缀名并保留前面的点号，例如 `.md`；`destination in files` 再检查目标是否属于发布文件集合。

#### 返回、None 与异常怎样改变顺序

调用一个函数时，运行环境会记住当前函数做完后要回到哪一处；这份“谁调用谁、完成后返回哪里”的记录叫调用栈。例如 `validate()` 调用 `heading_ids(...)`，后者执行 `return ids` 后，调用栈让程序回到 `validate()` 继续算 `fragment in ids`。`check(...)` 是另一次函数调用。

`True` 和 `False` 是布尔类型的两个值，分别表示真和假；原行 71 的 `fragment in ids` 会算出其中一个值。`check` 在条件为真时跳过错误分支，然后走到函数末尾。没有显式 `return` 的函数会正常返回特殊值 `None`，意思是“没有交回具体结果”，它不等于 `False`。调用者在这里不靠返回值判断是否成功，而是看 `check` 有没有抛异常。

异常表示正常语句顺序被打断。`raise ValueError(message)` 创建并抛出携带消息的错误；若当前调用链没有捕获它，程序就沿调用栈退回调用者，当前函数后面的语句不再执行。本脚本入口直接调用 `validate()`，本课这条路径没有捕获该错误，因此失败会退出这次检查，不是浏览器跳转或网络错误。

### 4. 端到端流程与本课边界

先把同一组假设值放在一起：当前 `path` 是 `ROOT/docs/start.md`，`relative` 是 `docs/start.md`，`content` 含有上面的链接，`target` 是 `guide.md#setup-1`，`files` 含有 `ROOT/docs/start.md` 和 `ROOT/docs/guide.md`，`texts` 保存了这两份文件的字符串内容。

真实处理顺序是：

1. `local_targets(content)` 发现 `guide.md#setup-1`；本课不把它的正则实现当成标题解析器。
2. `re.match` 看到目标没有 `scheme:` 开头，所以它不是此处跳过的外部链接。
3. `target.strip("<>")` 去掉包在目标外侧的尖括号；`unquote` 解码百分号编码；`partition("#")` 得到文件名 `guide.md`、分隔符 `#` 和片段 `setup-1`。
4. 从源文档的父目录拼出 `ROOT/docs/guide.md`，`resolve()` 规范路径；第 69 行确认它确实属于 `files`。
5. 目标后缀是 `.md` 且片段非空；脚本把 `texts[destination]` 传给 `heading_ids`。
6. `heading_ids` 返回集合。若 `setup-1` 在集合里，`check` 正常结束；若不在，`check` 抛出 `ValueError`，当前调用链停止。

这条路径只证明脚本按自身规则核对仓库文件和标题文字。它不会让浏览器跳转、不会请求外网，也不证明任何网页渲染器恰好采用相同的锚点规则。第 69 行先检查目标是否在发布文件集合里；如果文件缺失，错误发生在标题检查之前。

### 5. 真实源码逐段逐行精读

本章先说每段为何出现、输入从哪来，再展示完整的本段职责代码，最后沿实际值解释。代码块里的新增注释只作读码提示；代码后说明负责推导语法和结果，注释不能替代正文。

#### 5.1 `check`：把条件变成失败信号

##### 业务问题与实现思路

标题转换函数只回答“这段正文有哪些标题标识”，不决定某条链接能否通过。调用者先算出目标文件或片段是否存在，再把这个真/假结果和对应的错误消息交给 `check`。分工很小：`check` 只统一处理失败条件，标题函数与路径解析不混进来；条件成立时它自然结束，调用者继续。

##### 完整函数与固定提交位置

`scripts/validate.py` 中的 `check(condition, message)` 完整函数，原行 21–23，固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`：[对应源码行 21–23](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L21-L23)。

```python
def check(condition, message):  # 教学注释：定义接收判断值和错误消息的函数。
    if not condition:  # 教学注释：只有判断值为假时才进入缩进块。
        raise ValueError(message)  # 教学注释：抛出调用方传来的错误消息。
```

##### 原行 21–23：条件成立时继续，失败时抛错

`def check(condition, message):` 定义名字为 `check` 的函数，并声明两个形参。调用者必须提供一个条件值和一个消息值；定义阶段没有开始检查。冒号后的缩进让下面两行属于这个函数体。

`if not condition:` 先读取 `condition`，再由 `not` 把真变假、把假变真。只有结果为真时，才执行下一行缩进的语句。条件成立时这里不会返回 `True`；它只是跳过错误分支，然后函数到末尾正常结束，隐式返回 `None`。

`raise ValueError(message)` 用第二个实参创建错误对象并抛出。`ValueError` 是 Python 标准库提供的异常类型；这里的具体消息由调用方传入。抛出后，`check` 不会执行后续语句，也不会把布尔值交回调用点。调用方是否继续，取决于更外层有没有捕获异常；本链没有这样的捕获。

#### 5.2 `heading_ids`：把标题文字变成可查找的名字

##### 调用现场与输入准备

前一段调用代码先确认目标路径属于 `files`，然后从 `texts[destination]` 取出完整目标正文，把这段字符串作为唯一实参交给 `heading_ids`。本例正文含有 `Café, Tea!`、三个 `Setup` 和 `API_v2`。函数没有路径或片段参数，因此它只计算文本结果；比较 `setup-1` 是否出现仍由调用者负责。

##### 导入模块的源码与固定提交位置

`scripts/validate.py` 中的模块导入 `re`（原行 4），固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`：[对应源码行 4](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L4-L4)。

```python
import re  # 教学注释：导入标准库正则模块，并绑定到名字 re。
```

##### 原行 4：导入后才能用 `re` 名称找到模块工具

`import` 在这里把模块绑定到当前文件可用的名字 `re`；后面的 `re.findall` 和 `re.sub` 通过 `re` 找到模块里的函数。只导入模块不会运行 `heading_ids`；函数要等到调用表达式执行时才运行。

##### 完整标题函数与固定提交位置

`scripts/validate.py` 中的 `heading_ids(content)` 完整函数，原行 31–39，同一固定提交：[对应源码行 31–39](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L31-L39)。

```python
def heading_ids(content):  # 教学注释：定义接收文档文本的函数。
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)  # 教学注释：按行找标题并收集捕获到的文字。
    ids, counts = set(), {}  # 教学注释：分别创建最终标识集合和计数表。
    for heading in headings:  # 教学注释：按标题在文本中的顺序逐个处理。
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")  # 教学注释：小写、删除指定字符、修剪两端空白并替换普通空格。
        count = counts.get(slug, 0)  # 教学注释：读出这个基础名字此前出现次数，首次默认为 0。
        counts[slug] = count + 1  # 教学注释：把已经出现次数写回计数表。
        ids.add(slug if count == 0 else f"{slug}-{count}")  # 教学注释：首次用基础名字，重复项用旧次数加编号。
    return ids  # 教学注释：循环结束后把最终集合交还调用方。
```

##### 原行 31–32：接住正文并找到标题

`def heading_ids(content):` 定义标题转换函数。`content` 是形参，绑定调用时传进来的整篇字符串；这不是文件对象，也不是路径。函数签名只有一个参数，所以函数不会在这里知道源链接里的片段。冒号和缩进表明第 32–39 行属于函数体。

`re.findall(pattern, content, re.MULTILINE)` 在整个字符串里从左到右找所有不重叠匹配。模式的圆括号只捕获标题正文，因此它返回字符串列表。本例的结果是 `["Café, Tea!", "Setup", "Setup", "Setup", "API_v2"]`；井号本身不在捕获组里。`re.MULTILINE` 让 `^` 和 `$` 可在每一行的边界匹配；不带该标志时，`^` 只匹配字符串开头，`$` 匹配字符串结尾或末尾换行之前，因此这份多行正文不会逐行产生五个标题。点号依旧不跨换行，只有 `DOTALL` 才会改变这一点。

##### 原行 33–34：创建两种状态并按原序循环

`ids, counts = set(), {}` 先建立一个空集合和一个空字典，再按位置把它们分别绑定到 `ids` 与 `counts`。空花括号 `{}` 在这里表示字典；要得到空集合必须写 `set()`。`ids` 负责存最终可查名字，`counts` 负责记每种基础名字已经见过几次。它们是本次函数调用自己的可变容器。

`for heading in headings:` 每次把列表中的下一个标题文字绑定到 `heading`，然后执行缩进的第 35–38 行。列表保留标题出现顺序，因而第二个相同标题能看到第一个标题更新后的字典状态。循环结束后，缩进退回到第 39 行的函数体层级。

##### 原行 35：把一条标题逐步变成 slug

先执行 `heading.lower()`，生成小写字符串；本例的 `Café, Tea!` 变成 `café, tea!`，`API_v2` 变成 `api_v2`。这不是原地改写标题，字符串方法给出结果，随后把结果交给下一步。

`re.sub(r"[^\w\s-]", "", ...)` 对每个符合字符集合的字符用空字符串替换，效果就是删除逗号和感叹号。`strip()` 不带参数时去掉字符串首尾空白；它不会压缩中间连续空格。最后 `.replace(" ", "-")` 把每一个普通空格换成连字符。因此 `Café, Tea!` 最终成为 `café-tea`；若标题中间原有两个空格，代码会留下两个连字符。

点号把方法调用接到前一步的返回值上，整行从内到外求值，最后把最终字符串重新绑定到局部名字 `slug`。它没有直接修改 `heading`。此处理规则没有 Unicode 规范化或完整 Markdown 清理，所以“视觉相同”不保证生成相同名字。

##### 原行 36–38：旧计数决定后缀，集合保存可查名字

`count = counts.get(slug, 0)` 先读出这个基础 slug 的旧计数；第一次遇到 `setup` 时字典没有这个键，于是 `count` 是 `0`。`counts[slug] = count + 1` 随后把新计数 `1` 写入字典。**后缀使用本轮读出的旧 `count`，不是字典写回的新值**；第一次循环时，`count` 仍然是旧值 `0`。

下一条条件表达式 `A if condition else B` 会按条件选择一个结果。第一次 `count == 0` 为真，所以加入 `slug` 本身；第二个 `Setup` 读到旧 `count=1`，计数表先写入 `2`，然后加入 `f"{slug}-{count}"` 得到 `setup-1`；这里 `f` 前缀让花括号中的 `slug` 和 `count` 被当前值替换。`==` 比较两侧是否相等并产生真假结果，前一行的单个 `=` 则把右侧新次数赋给 `counts[slug]`，二者作用不同；第三个标题读到旧值 `2`，加入 `setup-2`。`ids.add(...)` 改动已有集合。它不返回“是否新加”的结果，也不保留加入顺序。

这两份状态不能混为一谈：字典保存次数，集合保存生成的名字。次数表可以让重复标题逐次编号；集合可以给调用者做成员检查。若只保留集合，第二次遇到 `Setup` 时它已经有 `setup`，但集合无法告诉代码应该接着用编号 1 还是 2。

##### 原行 39：循环结束后交回集合

`return ids` 的缩进位于 `for` 循环之外，所以它只在所有标题处理完成后执行一次。它把集合交还给调用点并结束这次函数执行；`counts`、`headings` 等局部名字不会随返回值一起交出。若输入没有匹配标题，循环执行零次，函数仍返回空集合。

#### 5.3 调用者：从链接目标走到通过或报错

##### 调用现场与输入准备

当前 `path` 是 `ROOT/docs/start.md`，`content` 是源文档正文，`relative` 是供错误消息使用的 `docs/start.md`；外层检查循环在原行 52–53 绑定这些值。`files` 和 `texts` 在原行 43–50 建立，`local_targets(content)` 在原行 26–28 找出当前目标。本例逐个跟踪的 `target` 是 `guide.md#setup-1`，目标文件位于 `ROOT/docs/guide.md`。这里展示从目标循环到片段成员检查的连续责任代码。

##### 完整调用责任与固定提交位置

`scripts/validate.py` 中 `validate` 的目标循环与条件（原行 64–71），固定提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5`：[对应源码行 64–71](https://github.com/zgozh/deep-codebase/blob/6d237d7c5665e0673b05b39bf072fceea112dcc5/scripts/validate.py#L64-L71)。

```python
        for target in local_targets(content):  # 教学注释：逐个处理当前文档发现的链接目标。
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):  # 教学注释：识别带 scheme: 前缀的目标。
                continue  # 教学注释：跳过此目标并开始本循环的下一轮。
            filename, _, fragment = unquote(target.strip("<>")).partition("#")  # 教学注释：清理外层括号、解码并按首个井号拆分。
            destination = (path.parent / filename).resolve() if filename else path  # 教学注释：相对当前文件目录定位目标，片段链接沿用当前文件。
            check(destination in files, f"Missing/unpublished link: {relative} -> {target}")  # 教学注释：先确认目标是发布文件。
            if fragment and destination.suffix == ".md":  # 教学注释：只对非空片段和 Markdown 文件检查标题。
                check(fragment in heading_ids(texts[destination]), f"Missing anchor: {relative} -> {target}")  # 教学注释：用目标文本生成标识并检查片段成员关系。
```

##### 原行 64–66：逐个取目标并跳过 scheme 地址

`for target in local_targets(content):` 调用提取函数并按返回顺序逐项绑定 `target`。当前源文件内容是 `content`，不是目标文件内容；此时还没查 `guide.md` 的标题。`local_targets` 只从内容里找它认可的 Markdown 链接目标，并会忽略标准三反引号代码围栏与行内代码；它不是浏览器或完整 Markdown 渲染器。

`re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)` 只尝试从目标开头匹配。方括号表示字符集合；第一组允许一个 ASCII 字母，后续 `[...] *` 允许零个或多个字母、数字、加号、点号或连字符，最后要求冒号。因此 `https:` 或 `mailto:` 这样的 scheme 会匹配，普通相对路径 `guide.md#setup-1` 不匹配。这个分支只跳过外部目标，不会请求它们。

命中时，`continue` 结束本轮循环并转到下一个目标，不执行本轮后面的文件和锚点检查。没有命中时则继续处理当前 `target`。`continue` 并不结束整个函数；它只影响最近一层循环。

##### 原行 67：先清理和解码，再按井号拆分

表达式从最里面开始：`target.strip("<>")` 去掉两端属于尖括号集合的字符；它不是一个完整的 URL 解析器。接着 `unquote(...)` 将 `%xx` 编码还原为文本。最后 `.partition("#")` 在第一个井号处分割。对当前目标，这些中间结果依次是 `guide.md#setup-1` 和 `("guide.md", "#", "setup-1")`。

左边的 `filename, _, fragment` 同时接收三元组的三项：`filename` 是 `guide.md`，`_` 接到分隔符 `#`，`fragment` 是 `setup-1`。下划线在 Python 中只是普通变量名；程序员常用它表示这个值之后不需要。若目标为 `#setup-1`，则 `filename` 是空字符串；若没有井号，`partition` 会把整个目标放在第一项，后两项为空字符串。

##### 原行 68–69：相对源文档定位目标并确认发布范围

条件表达式 `A if filename else path` 选择分支：本例 `filename` 非空，于是先读 `path.parent` 得到源文档所在的 `ROOT/docs`，再用路径的 `/` 操作符接上 `guide.md`，最后 `resolve()` 得到 `ROOT/docs/guide.md` 对应的绝对规范路径。如果 `filename` 为空，则该链接指向当前文档，直接使用 `path`。

`check(destination in files, message)` 先计算集合成员测试，再调用 `check`。本例的目标在 `files` 中，所以传入的条件是真，`check` 正常结束。若路径不在发布集合里，条件为假，第一段错误消息会抛出；执行流到此停止，不会继续读取 `texts[destination]`。`f"..."` 是格式化字符串：前缀 `f` 让花括号内的名字替换为当前值，所以这里的 `relative` 和 `target` 会填入源文档相对路径与原始目标文字。

##### 原行 70–71：仅为 Markdown 片段计算标题集合

`if fragment and destination.suffix == ".md":` 的 `and` 从左边先判断；片段为空时，右边不会再决定这个条件。当前 `fragment` 是 `setup-1`，而目标路径后缀是 `.md`，所以进入缩进块。无片段的普通文件链接仍经过上一行的文件存在检查；非 Markdown 文件即使带片段，也不会运行标题提取。

在第 71 行，Python 先计算传给 `check` 的两个实参。`texts[destination]` 按目标 `Path` 键取到目标文档字符串；该字符串传给 `heading_ids`，函数计算集合；`fragment in 集合` 返回布尔值；格式化字符串把源路径和目标拼成错误消息。最后这些值交给 `check`。即使条件为真，消息字符串也在调用之前构造，只是 `check` 不会显示它。

若 `check` 正常返回 `None`，原行 72 随后执行 `links += 1`，也就是把当前链接计数加一并存回去，然后循环继续。若 `check` 抛出异常，原行 72 不执行，当前函数和当前文档循环都不会再处理后续目标。

### 6. 关键机制与官方资料解读

下面用五个实际表达式看库规则怎样作用于本例的具体文字和状态。引用的官方页面都是 Python 3.15 文档；固定提交没有声明项目必须使用 Python 3.15，因此这些链接只说明所引用的语言规则，不证明项目的运行环境或实际执行结果。

#### 6.1 `MULTILINE` 怎样让五行标题都可匹配

原行 32 把整篇 `guide.md` 正文交给 `re.findall`，模式是 `r"^#{1,6}\s+(.+)$"`。字符串前的 `r` 让反斜线原样交给正则引擎。`^` 表示行首，`#{1,6}` 要求一到六个井号，`\s+` 要求至少一个空白，`(.+)` 捕获至少一个字符，`$` 表示行尾。圆括号只包住标题文字，所以后续拿到标题正文，不拿井号。

若不传 `re.MULTILINE`，`^` 只匹配整个字符串开头，`$` 匹配字符串结尾或末尾换行之前；对于有多行标题的这份正文，不能逐行找到五个标题。项目传入该标志后，`^` 和 `$` 也在各行边界匹配；点号仍不跨换行。于是捕获组依次得到 `Café, Tea!`、三个 `Setup` 和 `API_v2`，结果列表保留它们在文档中的顺序。`DOTALL` 才会改变点号能否匹配换行，本行没有使用它。[Python 3.15 `re.findall`](https://docs.python.org/3.15/library/re.html#re.findall)讲捕获组返回值；[`re.MULTILINE`](https://docs.python.org/3.15/library/re.html#re.MULTILINE)与[`re.DOTALL`](https://docs.python.org/3.15/library/re.html#re.DOTALL)分别说明这两个标志的作用。规则适用于这条模式，不代表代码理解了 Markdown 的全部语法。

#### 6.2 一条链式表达式怎样把标题变成名字

原行 35 收到 `heading = "Café, Tea!"`，先运行 `lower()` 得到 `"café, tea!"`。接着 `re.sub` 删除不属于字母、数字、空白或连字符的标点，得到 `"café tea"`；`strip()` 去掉首尾空白（此例没有），`replace(" ", "-")` 把普通空格换成连字符，最后得到 `"café-tea"`。逗号和感叹号被删，重音字母保留。

为看清嵌套调用的先后，下面把项目的一行写成等价的临时步骤；这些变量名是教学展开，不是项目源码：

```python
lowered = heading.lower()
cleaned = re.sub(r"[^\w\s-]", "", lowered)
trimmed = cleaned.strip()
slug = trimmed.replace(" ", "-")
```

Python 先算最内层 `heading.lower()`，把它的结果交给 `re.sub`；替换函数的结果接着交给 `strip`，再交给 `replace`，最后赋给 `slug`。每个字符串方法都产生新字符串，原来的 `heading` 不会被改写。`\w` 在默认 Unicode 字符串模式中包括 Unicode 字母数字和下划线，`\s` 包含空白；`re.sub` 把匹配项替换为空文字。官方对应说明分别见 [`str.lower`](https://docs.python.org/3.15/library/stdtypes.html#str.lower)、[`re.sub` 与字符类](https://docs.python.org/3.15/library/re.html#re.sub)、[`str.strip`](https://docs.python.org/3.15/library/stdtypes.html#str.strip) 和 [`str.replace`](https://docs.python.org/3.15/library/stdtypes.html#str.replace)。

这也说明一个边界：一个 `é` 可以作为单个预组字符，也可以由 `e` 加一个单独的组合重音符表示。两者看起来相同，但本模式会保留前者并删掉后者的重音符，可能分别得到 `café` 和 `cafe`。实现没有先把这两种字符组合规范成同一种写法，因此视觉相同的标题不保证名字相同。

#### 6.3 计数字典和标识集合保存不同状态

开始处理标题前，`counts` 是空字典 `{}`，`ids` 是空集合 `set()`。第一个 `Setup` 变成基础名字 `setup`：`counts.get("setup", 0)` 读出默认值 0，`count` 绑定到 0，随后字典改为 `{"setup": 1}`，集合加入 `setup`。

处理第二个 `Setup` 时，`get` 读出 1；局部名字 `count` 继续绑定这个旧值。字典项被重新赋为 2，并不会回头把局部 `count` 改成 2。条件 `count == 0` 因旧值是 1 而为假，`f"{slug}-{count}"` 拼出 `setup-1` 加进集合。第三个标题再经历 `2 → 3`，新名字为 `setup-2`。因此字典保存“每个基础名字出现几次”，集合保存“调用者能查哪些最终名字”。

`dict.get(key, default)` 在键不存在时给默认值；`set.add(value)` 把值加进集合，已存在的同值不会形成第二份。项目用这两个容器，是因为计数和成员检查是两种不同问题；只剩集合就无法知道接下来该编哪个号，只剩字典则不是要交给调用者做 `in` 检查的最终名字集合。[Python 3.15 `dict.get`](https://docs.python.org/3.15/library/stdtypes.html#dict.get)与[`set.add`](https://docs.python.org/3.15/library/stdtypes.html#set.add)分别说明这两项操作。

#### 6.4 解码文字、分开片段，再定位文件

本例原目标是 `guide.md#setup-1`。为了看出解码的作用，把同一目标改写为 `<guide%2Emd#setup-%31>`：它仍是本例的教学目标文字。`strip("<>")` 先得到 `guide%2Emd#setup-%31`；`unquote` 把 `%2E` 还原为点、把 `%31` 还原为数字 1，得到 `guide.md#setup-1`；然后 `partition("#")` 才按第一个井号给出 `("guide.md", "#", "setup-1")`。项目先解码再分割，后续把前后两段当作路径与片段。

`unquote` 只还原百分号编码，不联系远端地址；它也不会把 `+` 变成空格。`partition` 保留分隔符，并且只按第一次出现的位置切开。接着 `path.parent` 是 `ROOT/docs`，路径运算符 `/` 接上 `guide.md`，`.resolve()` 得到目标路径；`destination in files` 检查该路径是否属于本次发布文件集合。空文件名时，条件表达式直接沿用当前 `path`。只有目标在文件集合、片段非空且后缀为 `.md` 时，代码才从 `texts[destination]` 取正文。[Python 3.15 `urllib.parse.unquote`](https://docs.python.org/3.15/library/urllib.parse.html#urllib.parse.unquote)、[`str.partition`](https://docs.python.org/3.15/library/stdtypes.html#str.partition)、[`Path.resolve`](https://docs.python.org/3.15/library/pathlib.html#pathlib.Path.resolve)与[`PurePath.suffix`](https://docs.python.org/3.15/library/pathlib.html#pathlib.PurePath.suffix)分别支持这些操作说明。解码并按井号拆分仍只是本脚本的文字处理规则，不是完整 URL 解析器。

#### 6.5 返回值和异常怎样穿过调用栈

沿真实调用顺序看，`validate()` 先用 `texts[destination]` 调用 `heading_ids`。标题函数完成循环后执行 `return ids`，把集合交回调用点；接着调用者算 `fragment in ids`，再把真假值和错误文字传给 `check`。若成员测试为真，`check` 跳过 `raise`，正常走到末尾并隐式返回 `None`；调用者忽略这个无具体结果的返回值，继续到原行 72 增加 `links`。

若成员测试为假，`check` 执行 `raise ValueError(message)`，本函数此后没有正常返回。异常先退回 `validate()` 的调用位置；由于这条调用链没有捕获它，行 72 和后续目标循环都不会执行。`None` 是正常结束时“没有交回具体结果”的值，`False` 则是一个条件判断结果；二者不能混为一谈。[Python 3.15 `return`](https://docs.python.org/3.15/reference/simple_stmts.html#the-return-statement)、[`raise`](https://docs.python.org/3.15/reference/simple_stmts.html#the-raise-statement)以及[函数正常到末尾时的返回规则](https://docs.python.org/3.15/tutorial/controlflow.html#defining-functions)说明语言层面的控制流。这里的推演来自固定提交源码，不是脚本运行记录。

### 7. 同一组数据的正常与失败回放

#### 正常目标：命中后继续循环

先让 `heading_ids` 处理同一个 `guide.md` 内容。下表按文档顺序计算；计数写成“旧值 → 更新后的值”，所以加入重复编号时使用的是旧值：

| 标题文字 | 基础 slug | `count` 旧值 → 字典新值 | 加入 `ids` 的名字 |
|---|---|---:|---|
| `Café, Tea!` | `café-tea` | `0 → 1` | `café-tea` |
| 第一个 `Setup` | `setup` | `0 → 1` | `setup` |
| 第二个 `Setup` | `setup` | `1 → 2` | `setup-1` |
| 第三个 `Setup` | `setup` | `2 → 3` | `setup-2` |
| `API_v2` | `api_v2` | `0 → 1` | `api_v2` |

函数返回的集合包含 `café-tea`、`setup`、`setup-1`、`setup-2` 和 `api_v2`。集合不保证展示顺序；表格顺序来自输入标题列表，而不是集合。调用方拿到 `setup-1` 后，`fragment in ids` 为真，`check` 跳过 `raise`、正常返回 `None`，原行 72 才把 `links` 加一，然后同一源文件中的下一目标仍有机会检查。假设其余发布检查也通过，脚本会走到正常结束。

#### 失败目标：成员检查抛错并停在行 71

现在只把源文档目标改成 `guide.md#setup-9`。文件路径仍解析到同一个 `guide.md` 并通过文件成员检查，标题函数仍返回同一个集合，但 `setup-9 in ids` 为假。`check` 收到 `Missing anchor: docs/start.md -> guide.md#setup-9`，执行 `raise ValueError(message)`。异常发生在原行 71，因此原行 72 的 `links += 1` 没有执行；当前目标不计作成功，后续目标和后续文件检查也不会在本次调用中继续。

标题函数内部建立的 `headings`、`counts`、`ids` 都是运行时临时数据，返回的集合只用于这次成员判断；这条路径没有任何写文件语句，源文档和目标文档不会被改动。未捕获的异常沿 `validate()` 调用链退回脚本入口，结束本次发布检查。具体错误消息由检查代码构造；本课不推断运行环境怎样显示它。

#### 文件缺失与 scheme 跳过是另一条分支

若路径解析结果不在 `files` 中，先触发 `Missing/unpublished link`，标题函数还没运行。若目标带 `https:` 或 `mailto:` scheme，则 `continue` 跳过本地路径和标题检查；脚本没有验证这些地址是否可用。前者是文件成员条件失败，后者是代码主动跳过，都不代表浏览器行为。

#### 重复标题与自然编号的碰撞

计数器能区分相同基础标题，但不能保证最终字符串唯一。假设目标文件依次还有一个标题 `## Setup-1`：它的小写和清理结果本来就是 `setup-1`，而 `ids` 已经因为第二个 `Setup` 含有 `setup-1`。新标题这轮自己的 `counts["setup-1"]` 从 0 开始，仍会尝试加入同一个名字。集合会把相同字符串合并成一个成员，脚本看不出这两个不同标题发生了碰撞。

这与 `Setup` 重复三次的计数不是一回事：重复计数按基础 slug 记次数；碰撞是两个不同基础来源产生同一个最终字符串。成员检查只回答“集合里有没有 `setup-1`”，不回答它对应哪一个标题。当前脚本因而可能把一个有歧义的片段当成存在。

### 8. 设计取舍与使用/扩展方法

#### 为什么分开读文件、算标题和报告错误

固定提交里的 `heading_ids(content)` 只收文字并回集合，`validate()` 持有路径、`files`、`texts` 和错误消息，`check()` 负责在条件为假时抛错。这是从函数输入、输出和调用位置直接看到的责任边界，不足以证明原作者的主观动机。这样的分离让标题规则可以用给定正文单独推演：例如输入同一段 `guide.md` 正文，可以先检查 `setup`、`setup-1` 是否会生成，不必先打开路径或构造一条链接。它减少了测试标题转换时必须准备的文件系统状态；这是接口带来的便利，不声称项目已经有这类独立测试。

`counts` 和 `ids` 也各有职责。重复的 `Setup` 需要计数器从 0、1、2 生成不同后缀；调用方只需要对最终 `setup-1` 做成员检查。若只保留集合，重复次数消失；若只保留字典，调用方没有最终名字集合可查。这解释了当前两个容器一起出现的具体原因。

#### 轻量标题模式与同一 Markdown 渲染器的取舍

当前模式用行首井号匹配标题，执行简单，但不是完整的 Markdown 渲染器。比如正文中若有以三反引号开头和结尾的围栏代码块，里面写着 `# Setup`，`heading_ids` 仍会把那一行提取成标题；代码没有记录自己是否处于代码块中。另一种 Markdown 标题写法是先写 `Setup`，下一行再用 `-----` 作标记；当前正则要求行首井号，所以不会提取这种标题。标题中两个普通空格也会在替换后变成两个连字符。

若发布规则要求与网站最终显示的标题完全一致，可以选择网站采用的 Markdown 方言和对应渲染器版本，让检查复用相同解析规则。这样有机会减少“检查认为存在、页面却没有该锚点”的差异；代价是要引入并维护同一套解析器、配置和版本约束，而且渲染器升级可能改变已有锚点。这是基于当前边界的设计取舍，不是关于项目实际网站或原作者意图的事实。

#### 修改标题规则会影响已有链接

仅追踪原文中三个同名 `Setup` 对应的计数（下列状态省略 `Café, Tea!`、`API_v2` 等其他标题的字典项）。若把中间第二个标题改为 `Install`，这三个标题的序列是 `["Setup", "Install", "Setup"]`；按此序列更新后，`counts` 依次为 `{"setup": 1}`、`{"setup": 1, "install": 1}`、`{"setup": 2, "install": 1}`，生成名字为 `setup`、`install`、`setup-1`。**原链接 `guide.md#setup-1` 仍会通过成员检查，却会匹配第三个 `Setup`，而不是改名前的第二个标题**；若要继续指向改名后的第二个标题，应把链接片段改为 `#install`。修改大小写或字符清理规则也可能改变旧名字，因此任何转换规则变更都应先列出受影响的现有标题与链接，再一起迁移。

重复基础名的计数并不能解决不同标题产生同一结果的情况：已有两个 `Setup` 时再加 `Setup-1`，依然会产生相同的 `setup-1`。一种扩展设计是在加入候选名字前查 `ids`，若已占用就继续找下一个空名字；当前函数没有此步骤，也不会报告这种碰撞。增加该行为会改变过去可接受的名字，必须同时评估旧链接的指向和迁移方式。

#### 日常编辑如何进入发布检查

维护者编辑 `ROOT/docs/start.md` 的链接，或编辑 `ROOT/docs/guide.md` 的标题；脚本下一次读取这些文件时，会按固定规则重新计算目标和标题集合。成功检查只说明目标路径和片段满足脚本规则，不会改写任一文档，也不保证浏览器采用相同锚点。若新增语法支持，修改范围至少涉及链接目标提取或标题解析规则，并要拿重复标题、自然碰撞、百分号编码和缺失文件等具体输入核对行为；只改错误消息不会改变检查结果。

### 9. 易混淆点与带答案复习

**为什么 `heading_ids` 不收 `guide.md#setup-1`？** 调用者先把它拆成 `filename="guide.md"` 和 `fragment="setup-1"`，再用 `filename` 找到 `texts[destination]`。标题函数只收到目标正文，所以它能算出标识，却不知道哪条链接正在请求它；成员比较留在 `validate()` 中完成。

**第二个 `Setup` 为什么是 `setup-1`？** 第一次先读旧计数 0，字典随后保存 1；第二次读到旧值 1，字典更新为 2，但局部变量 `count` 仍是 1，于是格式化字符串生成 `setup-1`。第三次才读到旧值 2，生成 `setup-2`。

**为什么同时要 `headings`、`counts` 和 `ids`？** `headings` 是有顺序的列表，保留标题出现次序；`counts` 是字典，记录每种基础 slug 的旧次数；`ids` 是去重集合，供 `fragment in ids` 查询。只留 `ids` 无法知道重复标题的下一编号，只留 `counts` 则没有最终标识集合供调用者检查。

**`MULTILINE` 会让 `(.+)` 跨过下一行吗？** 不会。它只改变 `^` 和 `$` 对每行边界的判断；`.` 是否匹配换行由 `DOTALL` 控制，而原行 32 没有传入它。这样一行中的标题正文会被捕获，下一行仍由另一次匹配处理。

**`ids` 里有 `setup-1`，就能证明它对应第二个 `Setup` 吗？** 不能。若另一个标题本身是 `Setup-1`，它也转换成 `setup-1`；集合只保存一个相同字符串，不记录由哪个标题生成。成员检查会答“存在”，却不能辨认这个名字是否发生碰撞。

**`check` 通过时返回 `True` 吗？** 不会。传入的 `condition` 才是 `True`；`check` 跳过错误分支并走到末尾，按 Python 规则返回 `None`。调用者通过“未抛异常”继续执行原行 72，而不是读取 `check` 的布尔返回值。

**链接检查通过能证明浏览器会定位到第二个 `Setup` 吗？** 不能。这里的证据只到 `setup-1 in heading_ids(texts[destination])` 为真为止；它说明固定脚本自己的标题规则接受这个目标。没有验证浏览器或实际 Markdown 渲染器是否采用同一规则。

### 10. 本课收获、证据边界与下一课

这条真实代码路径的因果关系是：链接提取器给出目标文字，调用方识别外部 scheme、解码并分割片段、相对源文档解析目标路径、确认目标属于发布文件、读取对应文本、`heading_ids` 按行提取标题并转换名字、调用方检查集合成员，最后 `check` 正常返回或抛出异常。标题计数器使重复基础标题逐项编号；集合提供最终成员判断，但无法防止不同来源的名字碰撞。

源码依据固定为提交 `6d237d7c5665e0673b05b39bf072fceea112dcc5` 的 `scripts/validate.py`。官方机制说明链接到 Python 3.15 文档，但仓库没有在本例中声明必须使用这一 Python 版本。所有输入和路径都是静态教学假设；没有运行脚本、验证渲染结果或访问网络。本文没有讲完整的文件发现、其他发布检查或完整命令行。

可以接着读同一文件原行 26–28 的 `local_targets`，追问“它怎样从当前文档中筛出链接目标，为什么代码围栏中的例子会被忽略”；这会继续沿用本课的源文档与目标文档，不需要先读其他项目材料。

## 局部成品摘录：检查失败为何停止调用方

以下保留先前版本中有用的局部讲解，供对照局部来源展开；它不是完整课程，也不代表 v1.10.0 的完整正文布局标准。完整、自足的公开课程示范见上方十章主课。

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


## 局部成品摘录：重复标题怎样成为不同锚点

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
