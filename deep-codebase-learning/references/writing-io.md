# 原文保存、源码渲染与局部恢复

正文始终先保存为本课UTF-8原文part；默认single由当前会话编写，用户选择的宿主原生子作者只写其独占part，均不启动CLI作者或新模型。优先按宿主真实schema使用直接FREEFORM apply_patch或结构化edit；正文窄补丁可用安全quoted行数据，不把完整源码或整课重写进JS模板、String.raw、长Windows参数、base64或新转换器。普通字符串仍须转义；JSON.stringify、store/load只能处理已进入运行时的数据，不能修复执行前解析错误，不假设宿主未提供的JS/.NET API。

非源码章默认逐章专用扩写；第五章逐个已选5.x用Add写完整七位置及全部语义组到新的独占raw part，不合批多个5.x或多个重章来代替专用任务，已有draft/正确旧文作为只读基线迁入必要内容。首次原生patch就使用完整绝对目标路径，shell workdir不决定patch根；目标须未占用，不能套Add覆盖已有文件。已有稿局部勘误才用真实整行和短唯一锚Update，不能拿长行片段冒充整行或猜空白。下面仅展示新part的安全传输形状；普通双引号字符串用`\n`表示换行、`\"`表示正文双引号、`\\`表示正文反斜杠，Markdown反引号与补丁前缀都在字符串内：

~~~javascript
const partPath = "/path/to/project/.codelearn/写作/课ID/当前完整单元.md";
const result = await tools.apply_patch("*** Begin Patch\n*** Add File: " + partPath + "\n+这里替换为当前一个非源码章或单个5.x的充分正文，`inline`和\"双引号\"仍在字符串中。\n*** End Patch");
text(result);
~~~

这是实际正文写入形状，不是每篇必做的probe或逐行审批/计数任务；真实draft/part仍按原合同写足。仅此类宿主需要该JS包装，其他宿主仍优先实际提供的FREEFORM/结构化edit，不把示例强制到所有环境。

Windows读写明确UTF-8。Python的`-X utf8`不能修复PowerShell上游丢字节；必要管道仅在本命令作用域设`$OutputEncoding = [System.Text.UTF8Encoding]::new($false)`，不改全局profile。含Markdown反引号的Shell检索用安全字面量。patch的相对根不等于另一shell的workdir；首次保存必须从原定真实目标回读，不用外层同名文件冒充成功。

## 当前单元素材与source include

开写前实际读足以决定当前因果职责分组的源码，核真实路径、版本和1-based物理原行；网页展示行号不是源行。写正文时按当前表达式需要实际核适用官方规则并讲入推导，不把全套规则预读当开写前提，已核未变证据复用。上游实现按本课实际需要用已有读取能力取得已核版本的本地raw缓存，保留来源身份；渲染器只读本地文件，不联网、不猜版本或挑课。敏感值按隐私规则写明确脱敏示意，不能把秘密原样include；示意与真实源码分清，不为载体改真实quotes/comments、补闭合或缩代码。

新写/整体厚写源码单元执行[canonical正文任务](../assets/templates/stage-note.md#当前原行组的段落任务)，在当前上下文确定真实分组，随后将includes、组标题和充分正文一起保存到当前单个5.x的独占新raw part，不先落盘占位布局再逐段替换。容量不足可按内聚小节分批，不逐组机械新增调用。renderer的摘录范围H5不替代内部H6语义组及其各自解释量；组范围与真实闭合沿用canonical及教学合同，连续小块已有自动H5本组标题不重复。下面围栏只展示语法，实际part中的指令不放在围栏或inline代码里：

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

当前非源码章或单个5.x充分写入后的既有一次回读，结合现存原码或渲染结果，覆盖全部七位置、实际语义组及各自紧邻解释量，同时核类型/API签名、具体值、时机、返回和消费者；H5下不同H6行为不能用聚合量抵扣。当前聚焦单元已见缺口整批补齐后才接下一章/5.x，不每个原行组一个part；容量不足可在当前单元内按内聚小节保存。工具不评分、不删改叙事或源码，不设源码规模上限。解释正文按[原合同](teaching.md#试行扩写基线重要小节要展开到什么程度)的CJK区间U+3400–4DBF、U+4E00–9FFF计量，代码/标题/链接/重复不计；量与语义分开，不用整单元总量抵某组，不为几字差逐轮调用。raw总字符仅作诊断。

## 原文part装配与发布

原文part是唯一编辑和正式装配输入，是当前课的可恢复写作数据，不是任务卡、第二套教材或聊天transcript。part从开始就采用最终书结构：整书唯一H1、章H2、5.x H3、canonical七H4，不把每个part写成独立文章再合并修标题。Stage当前任务一段记实际raw顺序、current/next与未完范围，只渐进读当前必要part。最终顺序只选每章/单元当前有效版本，旧draft/旧part保留作基线；源码装配不把preview/candidate作parts输入，不重复装入正文，已审candidate仍可按下方纯字节方式发布。改章位置就调整明确顺序或修所属part；旧正确版本及结构性改写前完整raw/Git基线必须可恢复，不对正式整书做Note-Span、嵌套数组转string、JSON当正文或机械重排，不以摘要声称恢复。

不默认安排整稿/多raw的清空行、统一格式或重排句子脚本。真实表格/标题格式问题用现有唯一锚的native局部patch，保留已有内容；局部小修不新增备份。确需跨raw或整part结构格式变换，先保一次可恢复真实raw基线，按原保留规则核diff；rendered candidate不是raw基线。发现literal `\n`，不做全局replace反转义猜修，只从已核正确原始缓冲恢复；无法证明恢复时冻结并如实报告，不冒称原文完整。正常必要格式修正仍做，不能以避险牺牲可读性。

最终装配前一次汇总已知内容、数量和结构缺口，整批修所属单元；本批raw改动及范围自读完成后，Agent才用[assemble_note.py](../scripts/assemble_note.py)按明确顺序读raw parts，在同次装配中自动渲染源码并生成未占用candidate，不每改一句就重装整书；充分扩写齐后做最终装配。真正影响跨章/版式时再看candidate，不手动装配预览rendered、不保存派生缓存：

~~~text
python /path/to/skill/scripts/assemble_note.py --workspace /path/to/project/.codelearn --part 写作/课ID/01.md 写作/课ID/02.md --source-root /path/to/project --final-note notes/阶段/正式课.md --output 写作/课ID/candidate.md --min-lines 2000
~~~

source-root与final-note必须成对提供；后者是真实最终note的链接基准，不是candidate目录，真实路径仍限workspace。同次装配每个源文件只读一个raw缓冲，源码和去重source_refs的hash来自同buffer，短JSON返回include_count及这些对象。除include替换外，正文原字节、caller顺序和重复全部保留，part间只加两个LF；验证所有输入和范围后才创建输出父目录，不发布部分结果，元信息用ASCII JSON转义。不挑课、不评分、不裁剪。结合已核未变证据一次检查candidate全大纲、正文、来源/链接、UTF-8/围栏、正常行与原预算，标题检查保护围栏内源码注释，补未核范围和跨章衔接。必要修正汇总当前scope回raw part，再从raw重装配新candidate，只复读影响范围；不改预览或让作者重输出整章。

源码模式总include_count为零时，assembler在创建输出父目录/临时文件前返回`no_source_includes`，不发布candidate；无include的非源码稿使用不传source-root/final-note的纯字节模式。该guard只挡零展开，不检测全部正文损坏或教学质量；独立renderer内合法inline/fenced示意规则不变。

上例选普通完整课既有下限2000；本课若为复杂课，candidate与发布命令一致改用`--min-lines 3000`。assembler对最终读取/渲染/拼接后的物理行计量，显式正整数阈值不足返回`saved:false,error:below_min_lines,lines,min_lines`，在创建父目录/临时文件前退出，不改part或现存目标。成功仍用既有`saved:true`，传阈值时附`lines/min_lines`；未传保留旧行为及返回字段。此机械底线不判空行是否合法或教学质量，正常自然排版及反灌水仍独立审读。`below_min_lines`回所属薄章的专用扩写任务，整批缺口写完整part，不能先delivered再补正文。

新建完整课正式note，用同一assembler单part纯字节发布已审且通过本课阈值的candidate，不传source-root/final-note，不再渲染/读源，无额外分隔符：

~~~text
python /path/to/skill/scripts/assemble_note.py --workspace /path/to/project/.codelearn --part 写作/课ID/candidate.md --output notes/阶段/正式课.md --min-lines 2000
~~~

短答疑、用户明确窄例外、独立预览及充分旧文局部修沿原适用边界，不强加完整课min-lines；未传参数的API/CLI仍可用。修订已有完整课note先保真实完整raw或可靠Git基线，仅从通过同一阈值的已审candidate按现有纯字节能力覆盖，保留输入，不重抄正文或静默覆盖。最终note独立可读、全部真实源码及充分解释已入稿后，才可按安全所有权清理本次临时parts，不自动递归删历史。上述命令若经JS调用也复用普通quoted形状，不把PowerShell或Markdown反引号塞入JS模板，不新增probe。

已有note的完整基线已确认可恢复、candidate已核且完整课同阈值检查成功，两个实际绝对路径及覆盖权限均在本课授权范围内时，Windows宿主可直接纯字节复制（替换下面路径，不传source flags）：

~~~powershell
$candidatePath = 'D:/path/to/project/.codelearn/写作/课ID/candidate.md'
$notePath = 'D:/path/to/project/.codelearn/notes/阶段/正式课.md'
[System.IO.File]::Copy($candidatePath, $notePath, $true)
~~~

此调用保留candidate，不Move后再从源码重建。若复制失败，依据真实目标和已保基线恢复，不称发布成功；后续复核直接读现存candidate/note或沿用未变证据，不再render。

## state检查与保存失败

初次最低state与当前Stage须在首篇正文前建立；新建、相关JSON变化或新会话必要恢复时，对实际state运行[check_state.py](../scripts/check_state.py)：`python /path/to/skill/scripts/check_state.py /path/to/project/.codelearn/state.json`。只查v1结构，不迁移、不核路径或hash真实性、不提升掌握；保留合法旧v1可选/未知字段，按字段位置修必要差异，不因报错重建全套记忆。

这些少量本地机械辅助不启动服务或模型，默认源码渲染、整课装配及数量守门需要宿主已有Python 3.10+，由Agent使用。缺Python或安全文件提交能力时，可用宿主已有raw能力持久保存prepared草稿并继续答疑，准确报告正式交付未完成；不能绕过完整课既定数量及保存门槛，不安装依赖、不猜API、不退回危险全文转换或缩短教材。原文part先持久保存，工具失败不破坏输入或既有目标。

恢复按真实返回区分：请求解析/schema/范围错误先修当前输入，可换成宿主允许的合法传输；context mismatch先读当前影响范围，用真实整行和短唯一锚重建patch，不猜空白；权限/I/O/中断核真实保存边界。宿主policy拒绝不是普通解析/hunk错误，不能改用另一命令或工具绕过拒绝。失败保留原内容，不重试不变的坏请求，不以短摘要冒充恢复；无可靠保存方式就留draft、记录实际未写范围和返回点，不谎称成功。已有正确部分不全体回滚，独立答疑可继续。

按[记忆协议PERSIST](memory.md#post-turn-learning-commit)集中必要projections与一次影响范围V0，内部保存批次不各造learning event；真实有价值互动/中断仍及时最小checkpoint。V0只证明机械结构与保存，不证明教学、来源语义或学习者能力。
