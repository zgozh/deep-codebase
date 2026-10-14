# 成品教材与局部展开参照

供作者校准展开方式，判据以 [教学合同](teaching.md#唯一教学交付合同) 为准。下列旧片段与正反例用于观察局部逐句讲法，**不是十章整课交付标准，也不能拿一个短片段替代完整方法教学**。前两个 Python 片段来自本 Skill 仓库公开维护脚本；JavaScript/React 例子是虚构示意，不是目标项目源码、运行记录或真实学习者证据。静态示例未运行，不自称 validated。行号属于当时工作树，使用时重新核版本。

可复用的是逐句语法与机制、具体值和调用关系的讲法，Python、Promise、React 只是材料。完整课按十章骨架展开，第五章每个完整因果单元按固定五层写，所有贴出行都有对应解释。课程内容随项目技术栈/业务决定，没有前端不引入 React；示例事实与目标项目事实分别核实。旧片段中的自由段落不是取消稳定章节的例外。

## 完整示例课：从 Markdown 标题算出本地链接锚点

这篇课面向第一次读 Python 小脚本的人，只追一个具体问题：维护脚本怎样从 Markdown 文本收集标题标识，再检查本地链接里的片段是否存在。你不需要在自己的学习项目里使用 Python、Markdown、正则表达式或链接检查工具；这里的目标是示范如何把真实源码、输入、机制、中间值和调用结果连成一篇可独立阅读的课。

脚本事实来自公开仓库的准确相对路径 **scripts/validate.py**，固定在 [commit 265ae9900914a1c5ac5e9abccb1b821ab05eccae 的源码](https://github.com/zgozh/deep-codebase/blob/265ae9900914a1c5ac5e9abccb1b821ab05eccae/scripts/validate.py)。函数 heading_ids 原行是 31–39，真实调用在第 70–71 行，re 导入在第 4 行。每个代码块内以 `# 教学注释：` 标出的文字是为读者补充的说明，不属于仓库源码；其余语句保持原样，块后的逐行讲解完整保留。示例值是手工静态演算，不是运行记录，不代表 GitHub 或其他平台对 Markdown 的完整解析方式。

### 1. 业务场景与本课目标

设想仓库有一篇 guide.md，里面有几个同名标题；另一篇 Markdown 文件链接到其中一个标题。链接可能写成 guide.md#setup-1，井号后面的 setup-1 是要检查的片段标识。维护脚本要回答：按它自己的标题规则，目标文档是否包含这个标识？存在时检查继续；不存在时报告错误。

本课使用以下假设输入：

~~~markdown
# Café, Tea!
## Setup
## Setup
## Setup
### API_v2
~~~

第一行是一级标题，文字为 Café, Tea!；第二至第四行是文字相同的二级标题 Setup；第五行是三级标题 API_v2，下划线属于标题文字。为了手算，假设外层把这五行作为 Markdown 文本传给函数，并另有待检查片段 `setup-1`。链接不是传给 `heading_ids` 的标题输入。这组数据是教学输入，不能当作脚本运行证据。

学完后，你应能说明函数怎样收集标题、怎样把标题文字变成 slug、重复标题为什么生成编号、函数返回的集合由谁消费，以及当前实现有哪些适用边界。

### 2. 系统位置与架构分工

外层脚本负责取得文件文本并组织检查；函数是一段有名字、接收输入并交回结果、可在不同位置重复调用的语句；heading_ids 负责把文本变成一组可查找的标题标识；调用方负责用这组标识判断某个链接片段是否存在。“调用”是程序在某处写出函数名并提供输入，让函数开始执行；“返回”是函数把结果交回调用处。

这条数据链是：

guide.md 文本 → heading_ids(content) → 标识集合 → fragment in 集合 → check(条件, 错误消息)

箭头代表值被下一步使用，不代表网络或后台服务。heading_ids 不打开文件，也不解析链接；它只接收字符串并返回 Python 集合。真实调用把 texts[destination] 作为字符串传入，之后做成员判断，再把真假值传给 check。函数返回的集合只有经过调用方消费，才会影响链接检查结果。

本课精读从函数定义开始，到真实调用及 check 处理条件为止。外层其他文件遍历和链接解析不属于本例完整分析范围；这里解释调用接口中出现的值，不把外层职责说成函数自身行为。

### 3. 读懂本课所需的概念

Markdown 是用普通文本标记标题、列表和链接的轻量格式。本例的井号标题写法是在一到六个井号后跟空白，再写标题文字。例如 ## Setup 是二级标题。Markdown 还有其他标题写法；这段函数会不会识别它们必须看模式本身，不能凭“看起来也是标题”来推断。解析器是按一套格式规则读入文本并识别其中结构的程序；完整 Markdown 解析器会理解的不止井号标题，而本函数只按行匹配文本，没有构造完整文档结构。

slug 是把标题文字加工成短文本标识的常见叫法。本函数中 Setup 变成 setup；重复的 Setup 再变成 setup-1 和 setup-2。这里的 slug 只代表这个函数产生的值，不代表所有网页或 Markdown 平台都有同一规则。

正则表达式是描述文本匹配形状的模式。第 32 行的 ^ 表示行首，#{1,6} 表示一到六个井号，\s+ 表示一个或多个空白，(.+) 用圆括号捕获标题文字，$ 表示行尾。第 35 行的 [^\w\s-] 匹配一个不属于字母数字/下划线、空白或连字符的字符。前缀 r 表示 Python 原始字符串，让反斜线交给 re 按正则规则解释，而不是先由 Python 字符串转义。Unicode 是涵盖多种语言字符的字符标准；普通 Python 字符串模式中的 \w 默认匹配 Unicode 字母数字和下划线，\s 默认匹配 Unicode 空白；本函数使用 Python 默认字符范围。

列表是按位置保存多项值并保留顺序的容器；第 32 行产生的 headings 就是列表，因此同名标题按原文顺序编号。代码还用了字典和集合两类容器。字典 counts 将基础 slug 映射到次数，例如 setup: 2 表示已经遇到两个基础 slug 为 setup 的标题；它适合按键读取和更新值。集合 ids 保存不同的最终标识，例如 setup、setup-1、setup-2；它适合判断“某值是否存在”，不保存重复成员，也不表示顺序。一个记录次数，一个记录最终可查找的值。

局部变量是函数执行时存在于这次函数内部的名字，例如 heading、slug、count。return 会把后面的值交给调用点，并结束这次函数执行。此例最后返回 ids；counts 没有返回，所以调用方拿不到这次函数里的计数表。异常是用来报告非正常执行情况的信号；代码用 raise 抛出异常后，当前位置的常规语句顺序会被打断。ValueError 是 Python 自带的一类异常，在本例中表示链接片段没有通过检查；后面的 check 单元会展示这条失败路径。

### 4. 端到端流程与本课边界

在本课的假设中，外层已有 guide.md 的文本，也已取得 fragment = "setup-1"。文本传入 heading_ids；函数找到标题并逐项构造标识集合；调用方判断片段是否属于该集合；结果为真时 check 正常结束，为假时 check 抛出 ValueError。

顺序很重要：先从文档生成集合，再查一个链接片段。函数不会从 fragment 反推标题，也不会改写文档。它返回集合并不证明整份脚本成功，因为外层还可能检查其他链接或文件。本课只沿着这条具体调用链解释代码。

### 5. 真实源码逐段逐行精读

源码位置为 **scripts/validate.py**，固定版本 commit **265ae9900914a1c5ac5e9abccb1b821ab05eccae**；[该版本源码](https://github.com/zgozh/deep-codebase/blob/265ae9900914a1c5ac5e9abccb1b821ab05eccae/scripts/validate.py)可核对。下面每个单元按问题、真实源码、逐行讲解、具体回放和上下游关系展开。

#### 5.1 标题提取与标识生成

##### 5.1.1 问题与输入

函数要把一段 Markdown 文本变成一组标题标识。参数 content 来自调用者，假设值就是第一章的输入文本。函数需要 ids 收集最终结果，counts 记录每个基础 slug 已出现几次。它没有让调用者配置标题规则的参数，因此每次调用都使用代码里写定的规则。

##### 5.1.2 真实完整源码

正则模块 re 在文件第 4 行导入：

~~~python
import re  # 教学注释：导入 Python 标准库中的正则表达式模块，并在下文以 re 调用。
~~~

heading_ids 函数完整位于原行 31–39：

~~~python
def heading_ids(content):  # 教学注释：定义接收文本并返回标题标识集合的函数。
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)  # 教学注释：逐行找井号标题，取捕获组文本。
    ids, counts = set(), {}  # 教学注释：ids 存最终标识，counts 按基础 slug 保存出现次数。
    for heading in headings:  # 教学注释：按原文顺序逐个处理标题。
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")  # 教学注释：小写、删标点、去首尾空白，再把普通空格换成连字符。
        count = counts.get(slug, 0)  # 教学注释：读取本轮之前的次数；首次出现以 0 起算。
        counts[slug] = count + 1  # 教学注释：把下一轮可见的次数加一。
        ids.add(slug if count == 0 else f"{slug}-{count}")  # 教学注释：首次用基础值，重复项后缀用旧次数。
    return ids  # 教学注释：把集合交回调用方；计数表只在函数内使用。
~~~

##### 5.1.3 代码后的逐行解释

第 4 行 import re 将 Python 标准库模块绑定到名字 re。标准库是随 Python 一起提供的一组常用模块；后续的 re.findall 和 re.sub 通过这个名字调用正则查找和替换。这里没有导入 Markdown 解析库，所以代码的范围由简单文本模式决定。

第 31 行的 def 定义函数名 heading_ids。括号内 content 是形参，也就是接收输入值的名字；形参是在定义处声明的名字，实参是调用时传入的具体值。定义函数时不会处理任何文本；当调用者执行 heading_ids(某段文本) 时，括号中的文本实参才绑定到 content。冒号之后缩进的语句属于函数体。

第 32 行调用 re.findall(pattern, content, re.MULTILINE)：第一个实参给出匹配模式，第二个是要搜索的文本，第三个是匹配标志。模式只有一个捕获组，所以结果是捕获到的标题文本列表，不是整行匹配结果；列表按文本出现顺序排列。模式要求行首有一到六个井号，后面至少一个空白，再捕获至少一个字符直到行尾。MULTILINE 使 ^ 和 $ 按每行边界匹配。点号 . 默认匹配一个非换行字符，+ 要求前一模式至少出现一次；这里没有 DOTALL 标志（让点号也匹配换行的标志），所以捕获不会跨行。MULTILINE 改变行首/行尾的匹配位置，不改变点号规则。结果存入局部变量 headings。

第 33 行右侧创建两个空容器：set() 是集合，{} 是字典；左侧用逗号把它们分别绑定到 ids 和 counts。ids 保存最终标识，counts 保存基础 slug 的出现次数。两者都是这次函数调用的局部状态，不写文件，也不跨调用保存。

第 34 行开始 for 循环。每轮从 headings 列表按顺序取出一个文本，绑定给 heading，然后运行缩进的循环体。所有标题处理完后，程序才执行循环外的 return。这里保留先后次序，是因为同名项需要区分第几次出现。

第 35 行从 heading 计算基础 slug，并赋给局部变量 slug。调用 lower() 把大写字母转成小写；re.sub(pattern, "", text) 把匹配到的字符替换成空字符串，也就是删掉；strip() 去掉首尾空白；replace(" ", "-") 把普通空格换成连字符。点号表示对前一结果调用字符串方法，整条链从左向右求值。最后的替换只明确针对普通空格，不是所有空白。

第 36 行调用字典的 get(slug, 0)。第一个实参是要查找的键，第二个是键不存在时的默认值。第一次遇到某基础 slug 时会得到 0；后续遇到时得到之前保存的次数。count 保存的是本轮更新前的旧次数。

第 37 行计算 count + 1，再把新数写到 counts[slug]。方括号表示选中字典中对应键的位置。比如 slug 为 setup、旧 count 为 1 时，此行之后 counts["setup"] 为 2。变量 count 本身没有被这一行改写，仍然保留旧值供下一行判断。

第 38 行先计算条件表达式，再把其结果加入 ids。若旧 count 等于 0，就使用 slug 原文；否则使用 f-string，把 slug 和旧 count 放入形如 slug-数字 的字符串。add 把该字符串加入集合。算法意图让同一基础 slug 的重复标题获得不同后缀，但没有检查它是否与另一标题天然生成的 slug 碰撞；若两个标题得到同一个最终字符串，集合会只保留一个成员。集合不保证打印时按标题顺序排列。

第 39 行 return ids 把最终集合交给调用点并结束函数。它没有返回 headings、counts 或布尔值。因此调用方若要判断一个标识是否存在，仍需要自己进行成员判断。

##### 5.1.4 边界、副作用与本地回放

本函数内部只有 headings、ids、counts 和各轮临时变量；从展示代码看，它没有文件写入、网络访问或持久化副作用。第三章说明了这几个值的职责，第七章会逐轮演算。关键点是 count 是更新前的值：第三个 Setup 进入时 count 为 2，于是得到 setup-2，即使第 37 行随后把字典更新成 3。

##### 5.1.5 怎么用、上下游与实际接入

函数定义不会自行执行；真实调用在原行 70–71。调用方给文本，函数返回 ids，调用方对 ids 做成员判断。它不读取内部 counts，所以 counts 是实现重复编号的私有临时状态，ids 才是调用者实际使用的结果。如果删除 return，调用表达式就拿不到这个集合。

#### 5.2 用返回值检查片段

##### 5.2.1 问题与输入

得到标识集合后，外层要判断链接里的 fragment 是否存在。调用只在 fragment 有值且目标路径后缀为 .md 时进行。文本由外层先放入 texts 映射；texts[destination] 按路径键取得文本，它不是 heading_ids 自己读文件。

##### 5.2.2 真实调用代码与检查函数

以下是原行 70–71 的调用：

~~~python
if fragment and destination.suffix == ".md":  # 教学注释：只对非空片段且目标后缀为 .md 的链接继续检查。
    check(fragment in heading_ids(texts[destination]), f"Missing anchor: {relative} -> {target}")  # 教学注释：先取目标文本并生成 ids，再把成员判断和错误消息交给 check。
~~~

check 函数的定义位于同一文件原行 21–23：

~~~python
def check(condition, message):  # 教学注释：定义接收判断结果和错误文本的辅助函数。
    if not condition:  # 教学注释：条件为假时进入失败分支；为真则跳过。
        raise ValueError(message)  # 教学注释：抛出带调用方消息的异常，打断正常路径。
~~~

##### 5.2.3 代码后的逐行解释

调用片段第 70 行的 if 检查两个条件。fragment 是真值，并且 destination.suffix 与字符串 .md 相等时，才执行下一行。and 在左侧已经为假时不会继续求值右侧。路径后缀比较只是字符串条件，并不负责解析文件内容。

第 71 行从内向外求值：texts[destination] 先取得文本；文本传入 heading_ids；函数返回集合；fragment in 集合产生真或假；这个结果和错误消息一起传给 check。Python 在调用 check 之前先计算这些实参，因此成员测试先于 check 函数体执行。

f-string 中花括号里的 relative 和 target 会被调用环境当前的值替换。假设它们分别是 chapters/intro.md 和 guide.md#missing，消息会组合这两个字符串；这是说明格式化机制的假设，不是脚本运行时观测。

check 的定义行用 def 建立一个接收 condition 和 message 的函数。第 22 行用 not 反转 condition：如果它是假，进入缩进的 raise；如果它是真，则跳过 raise。函数到末尾时没有显式 return，因此正常完成返回 None，而不是 True。

第 23 行 raise ValueError(message) 创建并抛出异常，异常消息来自第二个参数。抛出会打断当前位置的正常执行顺序；check 不修改 Markdown，不生成标识，也不在这里捕获异常。本课没有展示外层的异常处理，因此不推断脚本其他位置会如何处理它。

##### 5.2.4 边界、副作用与本地回放

若假设 ids 包含 setup-1，成员测试为真，check 跳过 raise 并正常返回 None。若片段改成假设值 setup-3，成员测试为假，check 执行 raise ValueError(message)。这两条是基于具体值的静态推演，不是实测。

##### 5.2.5 怎么用、上下游与实际接入

真实数据交接是：外层传文本，heading_ids 返回集合，调用处把成员测试结果交给 check，check 负责把失败条件变成异常。若调用处只调用 heading_ids 而不测试成员，函数只会交还集合，不会自动报错；若不先算正确条件，check 也无法判断锚点是否存在。

### 6. 关键机制与官方资料解读

以下官方链接针对 Python 3.15 解释语言和标准库规则。引用文档版本是为了精确说明机制，不表示这个仓库实际使用 Python 3.15，也不要求读者项目使用 Python。

[Python 官方 re 文档](https://docs.python.org/3.15/library/re.html)说明了原始字符串、findall 的捕获组结果、MULTILINE 对 ^ 和 $ 的影响，以及 \w、\s、sub 的含义。对应本函数第 32 行，findall 收集捕获组文本；对应第 35 行，sub 替换匹配字符。正则表达式只匹配字符和位置，不知道某一行在文档语义上是不是一个链接目标标题。

[for 语句官方章节](https://docs.python.org/3.15/reference/compound_stmts.html#the-for-statement)说明循环逐项获取可迭代对象中的值并执行缩进代码块，这对应第 34–38 行。因为 headings 是列表，重复编号按文本顺序产生。[return 语句章节](https://docs.python.org/3.15/reference/simple_stmts.html#the-return-statement)说明 return 会结束当前函数并把表达式值交回调用处，对应第 39 行。

[字符串类型文档](https://docs.python.org/3.15/library/stdtypes.html#text-sequence-type-str)解释 lower、strip、replace 等字符串操作；相邻的 dict 和 set 章节解释映射与集合行为。这映射到第 33、36、37 行和 add：字典查次数，集合存最终标识。二者不是“都存很多值所以可互换”。

[f-string 官方章节](https://docs.python.org/3.15/reference/lexical_analysis.html#f-strings)解释了格式化字符串如何替换花括号中的表达式，对应重复标题后缀和错误消息。官方语言规则解释的是 Python 如何执行这些语句，不能据此证明不同网站使用相同 Markdown 规则。

### 7. 同一组数据的正常与失败回放

findall 从本课假设输入得到的标题列表，按代码规则手工演算为：

~~~text
["Café, Tea!", "Setup", "Setup", "Setup", "API_v2"]
~~~

Café, Tea! 先小写为 café, tea!；正则替换删除逗号和感叹号；strip 后仍是 café, tea；空格替换成连字符后为 café-tea。字符 é 没有被 [^\w\s-] 删除。API_v2 小写为 api_v2，下划线属于该模式允许的字符。

下表逐轮列出读到的标题、基础 slug、进入本轮时的字典和旧计数、写回后的字典，以及集合成员。花括号表示容器内容；特别是集合不承诺显示顺序。结果都是静态演算。

| 轮次 | heading → slug | 进入时 counts；旧 count | 写回后的 counts | 加入 ids；加入后 ids 成员 |
|---|---|---|---|---|
| 1 | Café, Tea! → café-tea | {}；默认 0 | {café-tea: 1} | café-tea；{café-tea} |
| 2 | Setup → setup | {café-tea: 1}；默认 0 | {café-tea: 1, setup: 1} | setup；{café-tea, setup} |
| 3 | Setup → setup | {café-tea: 1, setup: 1}；1 | {café-tea: 1, setup: 2} | setup-1；{café-tea, setup, setup-1} |
| 4 | Setup → setup | {café-tea: 1, setup: 2}；2 | {café-tea: 1, setup: 3} | setup-2；{café-tea, setup, setup-1, setup-2} |
| 5 | API_v2 → api_v2 | {café-tea: 1, setup: 3}；默认 0 | {café-tea: 1, setup: 3, api_v2: 1} | api_v2；{café-tea, setup, setup-1, setup-2, api_v2} |

第一轮没有 café-tea 这个键，所以 get 的默认值是 0；写回后次数为 1，最终标识不带后缀。第二轮为 setup 的首次出现，也得到 setup。第三轮读到旧次数 1，写回新次数 2，但仍用旧变量值 1 生成 setup-1。第四轮旧次数为 2，结果是 setup-2。第五轮的基础 slug 是新键 api_v2，所以旧值又从默认 0 开始。

最后返回集合内容为 {café-tea, setup, setup-1, setup-2, api_v2}。假设 fragment 为 setup-1，成员测试为真；若改为 setup-3，成员测试为假，check 会抛出已解释的异常。这里不声称真实运行脚本，也没有与 GitHub 的渲染结果比对。

### 8. 设计取舍与使用/扩展方法

字典和集合分工各有用途：只用集合就无法知道基础 slug 已出现几次；只用字典则调用方还得额外整理最终标识。当前实现用有序标题列表处理重复项，用字典保存计数，再把候选标识放入集合，适合快速做成员查询；但集合只能保存不同的字符串，不能证明每个标题都有独一无二的标识。

这个简化算法有一个可手算的碰撞边界。这里“碰撞”指两个不同标题最后算出同一个标识：

~~~markdown
# Setup
# Setup
# Setup-1
~~~

假设这三行是另一次传给函数的 Markdown 文本，以下仍是静态演算。第一行 `Setup` 生成基础 slug `setup`，旧次数 0，候选 `setup`；第二行同样生成 `setup`，旧次数 1，候选 `setup-1`；第三行的文字本身带 `-1`，所以它的基础 slug 已是 `setup-1`，该键的旧次数为 0，候选仍是 `setup-1`。第三行 `add` 时集合已经有同名字符串，因此不会新增第二个 `setup-1`。字典最终为 `{setup: 2, setup-1: 1}`，集合只有 `{setup, setup-1}` 两个成员，虽然输入有三个标题。

所以“重复基础标题通常会编号”不等于“算法保证所有最终锚点唯一”。若仓库必须让锚点与指定渲染器一致，需要选择或实现同一渲染规则，并测试这种自然后缀冲突；仅把结果装进集合只提供成员查询，不会修复冲突。

边界也从实现本身可见。模式要求一到六个井号、空白和非空标题，所以不会处理 Setext 写法——这种 Markdown 标题在文字下一行用等号或连字符标出级别；函数也没有先排除代码围栏，即用三枚或更多反引号或波浪号包住的代码块，因此其中恰好符合模式的行也可能被当标题。标点会按模式删除，普通空格替换成连字符；连续空格可能生成连续连字符，其他空白不一定被同样处理。因而这个函数不是通用 Markdown 解析器，也不能保证匹配所有平台的锚点生成法。

若实际需求要求与特定渲染器完全一致，应先明确目标解析器和版本，再选用相应解析实现并核对其行为；仅扩展这条正则不等于获得完整 Markdown 语义。若需求只是仓库内部有限规则的快速检查，这种实现较直接，但维护者应接受并说明输入边界。

### 9. 易混淆点与带答案复习

**问：headings 和 ids 都装很多文本，为什么不用同一种容器？**

答：headings 是列表，保留文本顺序，重复编号依赖这个顺序；ids 是集合，用来做成员判断。字典 counts 另负责记录每种基础 slug 的次数。第三轮的旧值 1 说明 setup 已出现一次，所以本轮得到 setup-1。

**问：第三个 Setup 为什么是 setup-2，不是 setup-3？**

答：count 记录本轮之前的出现次数。首次旧值为 0，第二次为 1，第三次为 2。第 37 行将字典更新为 3，但局部 count 仍是旧值 2，第 38 行据此生成 setup-2。

**问：return ids 是否也返回 counts？**

答：否。return 后只写 ids，所以调用者拿到的是集合。counts 只在函数内部辅助生成编号，没有被返回。

**问：fragment 在集合中时，check 返回 True 吗？**

答：不是。成员判断产生 True，并把它作为参数传入 check。check 在条件为真时跳过 raise，正常结束返回 None；条件为假时抛出 ValueError。这是三个不同的结果。

**问：这段代码证明所有 GitHub Markdown 锚点都能匹配吗？**

答：不能。它只展示这个函数对符合模式的文本如何生成字符串；没有调用 GitHub Markdown 解析器，也没有覆盖完整 Markdown 语法。

### 10. 本课收获、证据边界与下一课

你现在可以沿因果链解释源码：文本传给逐行正则查找，匹配结果按顺序进入循环；字符串方法形成基础 slug；字典记录重复次数；集合保存不同的最终标识；return 把集合交给调用方；成员判断再让 check 正常结束或抛错。第三个 Setup 得到 setup-2，是因为后缀使用本轮更新前的 count。

本课源码事实限于指定公开 commit 中的 re 导入、heading_ids 完整函数、真实调用和 check 函数；输入与每轮容器内容是静态假设。没有声称脚本已运行、没有声称学习者掌握，也没有把它说成通用 Markdown 解析器。后续可以沿调用者追踪 fragment、destination 和文本映射如何取得，再检查 validate 的其余流程。

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
