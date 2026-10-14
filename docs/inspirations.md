# 设计与文档来源

[返回 README](../README.md)

参考原项目的实际SKILL与README，而非仅目录名或市场描述。以下固定提交是最初设计与本次发布文档参考的可追溯版本；当前上游可能继续变化。本项目自行编写规则和文档，没有复制上游代码、HTML或模板，也不依赖其他Skill安装。

| 来源 | 采用的设计/文档组织 | 本项目的调整 |
|---|---|---|
| [ktaletsk/learn-codebase](https://github.com/ktaletsk/learn-codebase/tree/cbc0304609e76041f7f29b3ae9a1e3f1a16e07ad) | 主动回忆、渐进提示、持续认知记录；快速开始、例子、兼容性说明 | 分片 `.codelearn/`，证据等级、静默逐轮保存、阶段文章与重建 |
| [Eijnewgnaw/learning-codebases](https://github.com/Eijnewgnaw/learning-codebases/tree/07faad3974ee6238c42d119f6441d46c6134bb2c) | Flow、小证据集、事实/运行/文档/推断/未知分离；图、验证范围 | 不预设Python背景，主动诊断知识缺口、横向审计 |
| [kevinnio/tutor](https://github.com/kevinnio/tutor/tree/f0ad1ee514a034b720a4af4a36b5767f473a5994) | 学习者先尝试、验证真实结果、说明命令；安装/更新/贡献指南 | 学习目标仍在时优先引导，明确切换开发时尊重用户请求 |
| [yumeiriowl/code-learn-skill](https://github.com/yumeiriowl/code-learn-skill/tree/24bb238a57685cb3690bf8659228c9e8eaf25db8) | 语义代码段、图/术语、按需参考；用途与产物说明 | 按业务链渐进讲解，不整仓嵌入HTML；文章保留个人认知 |
| [PranitMohnot/repo-learner-suite](https://github.com/PranitMohnot/repo-learner-suite/tree/6f2a310318b58135eb80042e36dfe5b22a469e4c) | 一个推荐下一动作、自适应问题、课程与评审分离；产物结构/UX流程 | 不限Python notebook，不要求用户维护多命令或进度复选框 |

上述上游公开采用MIT许可证；本项目也采用 [MIT](../LICENSE)。引用表达设计来源，不表示上游作者背书、共同维护或授权测试结论。

Skill格式按 [Agent Skills规范](https://agentskills.io/specification)，安装命令按 [Skills CLI文档](https://github.com/vercel-labs/skills)。本机官方skill-creator用于创建指导及结构校验；公开维护者无需拥有本机的路径或工具。

## 公开教学方法的适配

### v1.11.0 完整功能教材的适配

本轮 Principal 实际读 [AOSA 的 A Simple Web Server](https://aosabook.org/en/500L/a-simple-web-server.html) 及其 [固定版本源码](https://github.com/aosabook/500lines/blob/fba689d101eb5600f5c8f4d7fd79912498e950e2/web-server/code/03-handlers/server.py)，采用从真实浏览器动作、服务器/库/项目处理器分工到文件读取和响应消费的完整功能尺度，作为自编十章主课的源事实。旧 helper 降为局部语法参照，不再用其十章齐全校准整个项目功能。该历史源码为 Python 2，不能无说明改成 Python 3 原文；[许可](https://github.com/aosabook/500lines/blob/master/LICENSE.md) 区分 MIT 代码与 CC BY 3.0 书文，主课自行写作，不大段翻译书文或复制插图。

本轮亦实际读 [Crafting Interpreters 的 Scanning 源章节](https://github.com/munificent/craftinginterpreters/blob/master/book/scanning.md)，取其具体输入、完整职责代码、局部机制与工程解释相连的教法，落到第五章原行推导和第六章机制展开。只适配组织思想，正文自编；书文/插图的 CC BY-NC-ND 4.0 与代码 MIT 区分，不翻译复用其书文或插图。以上是方法与源事实的来源，不能证明本 Skill 的学习效果；当前验收仍须只凭实际课程正文复演功能并核事实。

### 本轮 GitHub 源码对照

以下是2026-10-14读取当前 main 原源码后的设计适配，分支会继续变化；不是教学效果验证、热门度排名或上游背书，最初固定提交参照仍保留。

| 直接源码 | 实际机制 | 本项目取舍 |
|---|---|---|
| [Anthropic grader](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/grader.md) / [skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) | 实际产物和具体断言须有证据；表面遵守和弱判据会造成虚假信心，反馈应归纳成可复用指导并渐进披露 | v1.11.1 将详细合同、作者动作、质量状态和短证据各归一处；通读实际正文，少量定位/推导支持结论而不代替通读。不搬 JSON 评测基础设施、查看器或多轮盲测 |
| [Tutorial-Codebase-Knowledge nodes.py](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge/blob/main/nodes.py) 的 OrderChapters / WriteChapters | 用户重要内容和基础先于内部实现；编章时结合相关文件、上下文章节与前后课链接 | 按因果和概念依赖安排内容，使用当前局部上下文并保存接续点；不搬短源码摘录、固定词数、最大概念数或全仓上下文，不宣称稳定教学效果 |
| [deepwiki-open prompts.py](https://github.com/AsyncFuncAI/deepwiki-open/blob/main/api/prompts.py) 的 CODEMAP_SKELETON/ENRICH | 引用仅取已有上下文的真实路径/原行/片段；扩写不改原引用和步骤，不足不编 | 保留已确认源段与调用事实，例子另标；不搬两阶段JSON、全仓wiki/RAG依赖或其短段篇幅限制 |
| [awesome-copilot mentor](https://github.com/github/awesome-copilot/blob/main/agents/mentor.agent.md) | 搜调用用法，追问Why与取舍，以提示/苏格拉底式互动辅导 | 吸收用法搜证与取舍；不采用与默认详细独立教材冲突的短答、先问后放行 |
| [learn-codebase 当前 SKILL](https://github.com/ktaletsk/learn-codebase/blob/main/SKILL.md) | 学习journal、先预测再解释及短回复节奏 | 保留学习记忆；不搬150词上限或频繁下一步询问，不用提问阻止阅读 |

### 详细教材写法的本地参照与公开适配

v1.9.0 完整阅读本地 `replicate-learning` 的 Skill、批次全文/零件/概念词典模板、十七节节选、Java 与 Python 黄金例、通用方法、质量契约、阶段工作流与质量事故档案，提取写法后自行重写；该本地参照声明 Apache-2.0，采用其组织思路而非逐字复制。没有可确认的公开固定版本链接，因此不披露私人目录、宿主路径或未经核验的地址，也不称为公开可复现行为测试。没有复制其代码、教学事实或大段模板措辞。此前对本项目旧稿的静态接纳未满足用户最新反馈，v1.10.0 针对实际缺口继续适配，不把“黄金例”名称当质量证据。

| 参照中的具体设计 | 本项目 v1.9.0 的落点 | 有意调整 |
|---|---|---|
| 批次固定认知次序，把业务/架构放到源码前 | teaching 与 stage-note 的十章：场景/分工/基础/链路→精读→机制/回放/取舍/复习/接续 | 替换旧自由章节约定，自编十章而非照搬十七节；业务路线仍动态，不用章节数证明质量 |
| 逐件五层：问题、完整源码、逐行解释、边界、用法/接入 | 第五章每个完整因果单元的固定五层，源码后逐行或小组详细正文 | 完整方法或内聚职责足够，不强制无关整文件；所有贴出行对应解释，不以密度比例替代充分性 |
| 概念白话/类比与核心深潜，避免术语悬空 | 首次使用先短释，第三章及后来依赖前充分展开名称、机制、例子、区别和类比边界 | 完全零基础默认比参照更低；旧词只有真正充分讲过才回指，词典不能替代独立可读正文 |
| 零件也追为什么存在、来源、谁读、错值后果 | 配置/枚举/数据对象的实际值与读取链，脚本/测试对应输入、执行与断言 | 保留必要深度，真实不适用项说明理由，不制造每对象同款故障或插件 |
| 调用现场、上下游、实现与真实注册 | 第五章单元收尾与第八章使用/扩展，说明谁创建/登记/触发及漏接后果 | 不机械要求固定调用跳数、固定扩展步数或先改项目代码 |
| 底层穿透、最小手写示意、取舍与失败时间线 | 第六章官方规则与机制映射，第七章同一具体数据回放，第八章设计判断 | 示意明确非原文并说明生产边界；事实/历史/实测分别查证，不照搬样例中的泛化技术结论 |
| 事故显示全绿、裸行号、自检表仍可漏源码/机制/正文错误 | 一次语义通读分别判断事实与初学者可读，缺口直接修正文 | 不引入 gate 工具、质量 JSON、机械覆盖率、章数/词数指标、hash 仪式或反复全量复检 |

保留本项目的 `.codelearn/` 持久化、横向审计、真实能力证据和独立重建，不采用参照的自动开发/提交/运行义务或以阅读替代能力验收。公开教学材料与规则不能证明模型稳定遵循，也不能保证读者掌握；固定骨架只减少遗漏机会。

v1.11.1 再读本地批次模板第⑥节，复用完整代码、逐行解释、机制、怎么用及上下游接入的教学职责；这些要求归入唯一教学合同，不复制十七章节、闸门工具或字数规则，也不因精炼 Skill 而缩减教材深度。

v1.10.0 另实际查阅 [Write your Own Virtual Machine](https://www.jmeiners.com/lc3-vm/)、[Diátaxis Explanation](https://diataxis.fr/explanation/) 与 [Diátaxis Tutorials](https://diataxis.fr/tutorials/)。前者将概念、真实代码、执行机制和使用连接起来，适配为完整因果单元；不采用允许跳过核心原语的建议，因为本 Skill 默认零基础。Explanation 强调联系、上下文、原因和例子，适配为架构及机制判断；Tutorials 的具体有意义进展适配为每课一个因果目标，但其避免解释的分工不直接用于本 Skill 的综合教材。以上是教法组织的推论，不是效果保证，也不复制原文。

以下是原方法作者、官方教育材料或维护者资料支持的设计取舍，不是本 Skill 教学效果的试验报告。来源内容由导师消化进当前教学，不要求学习者先读这些教材。

| 原始来源 | 它实际说明什么 | 本 Skill 的具体适配 | 限制 |
|---|---|---|---|
| [NSW：Cognitive load theory in practice](https://education.nsw.gov.au/about-us/education-data-and-research/cese/publications/practical-guides-for-educators/cognitive-load-theory-in-practice) 的 Summary / Teaching strategies | 完整示范、随熟练程度增加独立解决、去除无关信息并将必要信息放在一起 | 一个因果目标、源码紧邻解释、完整示范到带提示小步再到独立变式；收广度不删必要深度 | 学校教学实践与研究综合，不是成人大型代码库或本 Skill 的直接实验 |
| [PRIMM 原作者说明](https://primmportal.com/) | 阅读/追踪先于写作，Investigate 可用注释与追踪，Modify 从小变化扩展，Make 转向新程序；无需每课完整五步 | 已教材料上的小修改，再到独立实现；只吸收梯度，不用 Predict 让零基础猜陌生源码 | 教师提供的小程序与未知真实仓库不同；本 Skill 先教后问规则优先 |
| [MDN LocalLibrary](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Express_Nodejs/Tutorial_local_library_website) 的 Overview / The LocalLibrary website | 先交代目的、能力与范围，从只读目录扩展到数据/表单，贯通数据、路由、显示与部署 | 问题→能力→架构→代表完整链→其他能力与横向审计 | 人工编排且有前置的 Web 教程，不是任意项目固定顺序 |
| [MDN Dealing with files](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files) 的 Prerequisites / Learning outcomes / Manipulating files | 文件夹、路径、扩展名与文件操作也是明确学习目标，并有操作系统前提 | 第一次读实际文件/运行命令时解释读法、工作目录与工具，不只讲编程语法 | 不照搬 Web 目录，也不要求先读完教材或先上长基础课 |
| [AOSA 目的](https://aosabook.org/en/) 与维护者写的 [Bash 3.1–3.3](https://aosabook.org/en/v1/bash.html) | 作者解释组件、交互和取舍；Bash 从终端/文件输入经解析到执行及返回状态，再展开子系统 | 架构/业务双地图与真实调用/状态/返回链，适用于 CLI 和库 | 历史作者说明不证明当前仓库同版本实现；不作为零基础必读门槛 |
| [CS50 Final Project](https://cs50.harvard.edu/x/project/) 的 Getting Started / How to Submit | 学习者设计实现产物、安排合理范围/里程碑、展示作品并解释选择 | 独立 Mini Version、真实产物/能力证据与设计对比，区分定向和完整完成 | 完整课程后的结业要求，不是第一课门槛；不能以其证书标准为本 Skill 背书 |

这些映射是方法适配推论。没有方法流行度排名、效果倍数或真实学生成功保证；无需将外部课程安装为运行依赖。
