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

v1.8.0 继续详细参考 `replicate-learning` 的实际 Skill 6.1/6.4、批次全文模板、逐句黄金样例、质量契约与事故档案：采纳源段保真、代码后逐句因果展开、调用现场/上下游/接入和失败时间线；在本项目按因果小课组织，吸收其具体场景、逐句三问、调用现场与机制/手写示范/取舍的展开密度。原项目采用17节章法，本项目只吸收详细展开方式，不复用其章法或提供固定章节模式；备课和审核移出正文。未复制其工具或模板，也未采用整仓固定覆盖百分比、所有对象同等深度、固定反例/迭代数量、强制应用运行或 Vibecoding 开发义务。规则多也能组织完整详细教材；已知退化不能单独归因为规则长度。本项目精简不产出教学价值的重复动作，不缩讲解。该本地参照不是运行依赖、公开可复现测试结果或质量保证。

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
