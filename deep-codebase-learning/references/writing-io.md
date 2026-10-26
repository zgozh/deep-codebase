# 原文保存、源码渲染与局部恢复

正文始终先保存为本课UTF-8原文part；默认single由当前会话编写，用户选择的宿主原生子作者只写其独占part，均不启动CLI作者或新模型。优先按宿主真实schema使用直接FREEFORM apply_patch或结构化edit；正文窄补丁可用安全quoted行数据，不把完整源码或整课重写进JS模板、String.raw、长Windows参数、base64或新转换器。普通字符串仍须转义；JSON.stringify、store/load只能处理已进入运行时的数据，不能修复执行前解析错误，不假设宿主未提供的JS/.NET API。

在functions.exec中调用tools.apply_patch时，下面是可直接模仿的新draft/当前part保存形状：先将partPath换成本批已确认、未占用的真实完整目标路径；已有part用实际局部Update，不能套Add覆盖。普通双引号字符串用`\n`表示换行、`\"`表示正文双引号、`\\`表示正文反斜杠，Markdown反引号直接作为数据：

~~~javascript
const partPath = "/path/to/project/.codelearn/写作/课ID/draft.md";
const result = await tools.apply_patch("*** Begin Patch\n*** Add File: " + partPath + "\n+# 当前课草稿\n+\n+正文：`inline`、\"双引号\"、路径 C:\\demo\\file.txt。\n+\n+```text\n+\tcode \"quoted\" C:\\demo\\file.txt\n+```\n*** End Patch");
text(result);
~~~

这是实际正文写入形状，不是每篇必做的probe或逐行审批/计数任务；真实draft/part仍按原合同写足。仅此类宿主需要该JS包装，其他宿主仍优先实际提供的FREEFORM/结构化edit，不把示例强制到所有环境。

Windows读写明确UTF-8。Python的`-X utf8`不能修复PowerShell上游丢字节；必要管道仅在本命令作用域设`$OutputEncoding = [System.Text.UTF8Encoding]::new($false)`，不改全局profile。含Markdown反引号的Shell检索用安全字面量。patch的相对根不等于另一shell的workdir；首次保存必须从原定真实目标回读，不用外层同名文件冒充成功。

## 当前单元素材与source include

先实际读当前因果职责必要源码及适用官方规则，核真实路径、版本和1-based物理原行；网页展示行号不是源行。上游实现先用已有读取能力取得已核版本的本地raw缓存，保留来源身份；渲染器只读本地文件，不联网、不猜版本或挑课。敏感值按隐私规则写明确脱敏示意，不能把秘密原样include；示意与真实源码分清，不为载体改真实quotes/comments、补闭合或缩代码。

作者按[唯一5.x骨架](../assets/templates/stage-note.md#5x-真实符号本单元具体行为)写足本单元叙事，在4–5区域每个实际源组处放一条独立include，紧接该组充分解释；不手抄源码或再造原行标题。下面围栏只展示语法，实际part中的指令不放在围栏或inline代码里：

~~~markdown
<!-- codelearn-source {"path":"cmd/root.go","first":43,"last":49,"language":"go","title":"登记输入"} -->
~~~

将示例替换为本项目实际文件、真实范围、语言和行为；当前章请求同时写明每组要讲的表达式/具体值/机制及原预算。编写态include不是教材正文；最终note必须有全部真实源码、代码后的H5原行标题与充分正文，不留未解析标记。

## 渲染当前part

代表性完整单元需要预览校准时，Agent可调用内置[render_sources.py](../scripts/render_sources.py)，学习者无需运行；预览不是正式装配输入，日常只编辑raw part：

~~~text
python /path/to/skill/scripts/render_sources.py --workspace /path/to/project/.codelearn --source-root /path/to/project --input 写作/课ID/unit.md --output 写作/课ID/unit.rendered.md --note notes/阶段/正式课.md
~~~

input/output/note的真实路径限workspace，源码限source-root；note是最终链接基准，可尚不存在。输出必须是新文件，所有输入/范围验证后工具才创建输出父目录，坏源码/越界不提前建目录。工具按同一原始缓冲生成原码、动态围栏、代码后H5及真实相对链接，保留tab、空行、原注释、引号和其他叙事原字节；围栏内示意标记保持字面，处理非递归。短JSON给include_count和标准对象型source_refs：path、symbol:null、revision:null、整文件真实SHA256、evidence_kind:code；元信息用ASCII JSON转义，json.loads后Unicode路径准确，教材正文不因此转义。直接复用这些元信息，不手造hash或新建账本。

渲染成功仍须同次实际回读本单元全部七位置与源码组，核类型/API签名、具体值、时机、返回与消费者，以及紧邻解释量；工具不评分、不删改叙事或源码，不设源码规模上限。解释正文按[原合同](teaching.md#试行扩写基线重要小节要展开到什么程度)的CJK区间U+3400–4DBF、U+4E00–9FFF计量，代码/标题/链接/重复不计；量与语义分开，不用整单元总量抵某组，不为几字差逐轮调用。raw总字符仅作诊断。

## 原文part装配与发布

原文part是唯一编辑和正式装配输入，是当前课的可恢复写作数据，不是任务卡、第二套教材或聊天transcript。part从开始就采用最终书结构：整书唯一H1、章H2、5.x H3、canonical七H4，不把每个part写成独立文章再合并修标题。Stage当前任务一段记实际raw顺序、current/next与未完范围，只渐进读当前必要part。改章位置就调整明确顺序或修所属part；旧正确版本及结构性改写前完整raw/Git基线必须可恢复，不对正式整书做Note-Span、嵌套数组转string、JSON当正文或机械重排，不以摘要声称恢复。

本批raw内容改动及范围自读完成后，Agent才用[assemble_note.py](../scripts/assemble_note.py)按明确顺序读raw parts，在同次装配中自动渲染源码并生成未占用candidate，不每改一句就重装整书；充分扩写齐后做最终装配。真正影响跨章/版式时再看candidate，不手动装配预览rendered、不保存派生缓存：

~~~text
python /path/to/skill/scripts/assemble_note.py --workspace /path/to/project/.codelearn --part 写作/课ID/01.md 写作/课ID/02.md --source-root /path/to/project --final-note notes/阶段/正式课.md --output 写作/课ID/candidate.md
~~~

source-root与final-note必须成对提供；后者是真实最终note的链接基准，不是candidate目录，真实路径仍限workspace。同次装配每个源文件只读一个raw缓冲，源码和去重source_refs的hash来自同buffer，短JSON返回include_count及这些对象。除include替换外，正文原字节、caller顺序和重复全部保留，part间只加两个LF；验证所有输入和范围后才创建输出父目录，不发布部分结果，元信息用ASCII JSON转义。不挑课、不评分、不裁剪。结合已核未变证据一次检查candidate全大纲、正文、来源/链接、UTF-8/围栏、正常行与原预算，标题检查保护围栏内源码注释，补未核范围和跨章衔接。必要修正汇总当前scope回raw part，再从raw重装配新candidate，只复读影响范围；不改预览或让作者重输出整章。

新建正式note可继续用同一assembler仅传`--part candidate.md`，不传source-root/final-note，原字节独占发布，不再渲染或读源，无额外分隔符。修订已有note先保一份真实完整raw或可靠Git基线，再用宿主已有安全raw发布能力替换；不让模型重抄正文，不静默覆盖。最终note独立可读，全部真实源码及充分解释已入稿后，才可按安全所有权清理本次临时parts，不自动递归删历史。上述命令若经JS调用也复用普通quoted形状，不把PowerShell或Markdown反引号塞入JS模板，不新增probe。

已有note的完整基线已确认可恢复、candidate已核，且两个实际绝对路径及覆盖权限均在本课授权范围内时，Windows宿主可直接纯字节复制（替换下面路径，不传source flags）：

~~~powershell
$candidatePath = 'D:/path/to/project/.codelearn/写作/课ID/candidate.md'
$notePath = 'D:/path/to/project/.codelearn/notes/阶段/正式课.md'
[System.IO.File]::Copy($candidatePath, $notePath, $true)
~~~

此调用保留candidate，不Move后再从源码重建。若复制失败，依据真实目标和已保基线恢复，不称发布成功；后续复核直接读现存candidate/note或沿用未变证据，不再render。

## state检查与保存失败

初次最低state与当前Stage须在首篇正文前建立；新建、相关JSON变化或新会话必要恢复时，对实际state运行[check_state.py](../scripts/check_state.py)：`python /path/to/skill/scripts/check_state.py /path/to/project/.codelearn/state.json`。只查v1结构，不迁移、不核路径或hash真实性、不提升掌握；保留合法旧v1可选/未知字段，按字段位置修必要差异，不因报错重建全套记忆。

这些少量本地机械辅助不启动服务或模型。缺Python或文件系统不支持安全提交时，用宿主实际等效raw能力或准确报告限制，不安装依赖、不猜API、不退回危险全文转换或缩短教材。原文part先持久保存，工具失败不破坏输入或既有目标。

恢复按真实返回区分：请求解析/schema/范围错误先修当前输入；context mismatch只读当前局部并用短唯一锚重建有效patch；权限/I/O/中断核真实保存边界。失败保留原内容，不重试不变的坏请求，不以短摘要冒充恢复；无可靠保存方式就留draft、记录实际未写范围和返回点，不谎称成功。已有正确部分不全体回滚，独立答疑可继续。

按[记忆协议PERSIST](memory.md#post-turn-learning-commit)集中必要projections与一次影响范围V0，内部保存批次不各造learning event；真实有价值互动/中断仍及时最小checkpoint。V0只证明机械结构与保存，不证明教学、来源语义或学习者能力。
