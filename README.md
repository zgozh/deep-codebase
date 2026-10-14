# Deep Codebase Learning

**在 AI 的长期引导下，学会解释、修改、定位问题，并独立重建一个真实项目的核心系统。**

[English](README.en.md) · [使用指南](docs/usage.md) · [设计与记忆](docs/design.md) · [验证与限制](docs/validation.md) · [贡献](CONTRIBUTING.md)

`deep-codebase-learning` 是一个 Agent Skill。默认以**详细、可独立阅读的初学者教材**带你学习真实业务链，聊天简短给范围与笔记链接，并随时答疑。进度保存在目标项目 `.codelearn/`，固定会话或换会话都能继续。当前版本 1.8.1。

> Flow before files. Understanding before coverage. Evidence before mastery. Reconstruction before completion.

## 快速开始

需要一个支持 Agent Skills、能读取真实项目源码、写入学习记忆并访问相关官方资料的编码 Agent。先准备要学习的项目本地副本，在该项目目录打开会话；这不是只输入项目名就能教学的在线课程。Skill 运行不需要 Node、Python、数据库、MCP 或后台服务；下面的安装器需要 Node.js/npm。未装目标项目依赖也能静态读码，尚未运行的机制保留未验证。

用 [Skills CLI](https://github.com/vercel-labs/skills) 安装：

```bash
npx skills add zgozh/deep-codebase --skill deep-codebase-learning -g -a codex
```

这里 `-a codex` 限定 Codex，其他宿主按安装器选择；`-g` 是用户级安装，去掉则安装到当前项目。先查看、不安装：

```bash
npx skills add zgozh/deep-codebase --list
```

随后在要学习的源码项目打开新会话，说：

```text
带我深度学习这个项目。
```

在当前会话或以后同一个项目的新会话说：

```text
继续学习。
```

如果没有自动选中 Skill，在 Codex 中显式说 `使用 $deep-codebase-learning 带我学习当前项目`。其他 Agent 的显式调用方式由其产品决定。手动复制安装和 Windows 步骤见 [使用指南](docs/usage.md)。

已配置GitHub SSH、但本机HTTPS访问不可用时，可将安装源替换为 `git@github.com:zgozh/deep-codebase.git`。也支持下载后从本地目录安装。

### 零基础也可以直接这样说

```text
使用 $deep-codebase-learning 带我从零深度学习当前项目。我没有编程经验，请先讲它解决什么问题，再就地解释读源码需要的基础。
```

默认已经详细，无需额外口令。第一次需要时解释项目根、相对路径、源行、定义/调用及命令怎么操作，不要求先学通识或自行补读官方资料。可只读完整教材，愿意时练习并验证能力。首次会提供一次单会话/委派编写选择；未选择保持单会话，不阻塞首节。随时可复制：

```text
继续学习，接着当前代码和因果问题讲。
使用单会话模式编写教材。
使用主会话规划与审查、子 agent 编写教材的模式。
这节请在聊天完整讲解。
这段仍太浅，请把所有当前新概念、重要语句和官方资料带着详细讲，并保存这个偏好。
总结当前主题。
总结当前阶段。
总结当前会话。
先继续讲解，暂时不要让我作答；能力未验证照实保留。
先切到开发任务：修复这个问题，并保存学习返回点。
重新读取 $deep-codebase-learning 的最新 SKILL.md 和相关协议，保留当前进度继续学习。
```

| 目标 | 可获得的内容与完成边界 |
|---|---|
| 快速了解项目 | 问题、能力、模块分工和一条可定位流程；不等于已读懂实现 |
| 深度学习实现 | 真实注释源码、当前必要基础、调用/状态/失败与设计取舍；按小目标连续推进 |
| 完整验证能力 | 完整 Inventory 与横向审计、真实独立能力和可运行 Mini Version；仅全景完成不能记 PROJECT_COMPLETE |

不承诺几分钟达到作者级能力，也不绑定模型/档位。子 agent 是可选工作方式，不是依赖；现有证据及未验证范围见 [验证文档](docs/validation.md)，不能从一个修订样本给模型或所有项目做效果保证。

## 学习过程中会发生什么

CLI 安装后可用 `npx skills update deep-codebase-learning -g` 只更新本 Skill，项目级安装改用 `-p`。当前安装器为 Codex 选择的全局目录是 `~/.agents/skills`；手动目录与宿主配置可能不同，以实际发现结果为准，不自动删除或移动重复安装。更新 Skill 文件不删除目标项目的 `.codelearn/`。详见 [安装与更新](docs/usage.md)。

**始终默认你是初学者。** 不预设你了解项目功能、概念、架构、语言特性、框架或底层原理。导师根据实际仓库主动安排完整路线，先解释系统解决什么问题和必要概念，再逐步读业务链与源码。你不需要自己找知识缺口或决定下一步；已经通过独立表现证明的知识可减少重复讲解，其他未验证知识仍按初学者讲。

**详细笔记是默认完整课堂，聊天随时答疑。** 首节先写项目问题、能力、模块边界与白话流程，再按真实功能逐层读源码，有前后端贯通。每节实际编写、核对教材，再简短给范围与可点击路径；不是只列文件、承诺以后讲，也不在聊天重复全文。你问某行/术语/框架就直接充分解惑；只有明确完整聊天课堂请求才展开整节。实质教材缺漏同步修订。无需先答陌生题、确认理解或回复“继续”才能阅读。

**源码教材讲实现，不能停在职责概述。** 本节先给具体业务问题和最少必要背景，再展示实际读取的源码路径、符号及原行号/可靠定位。重要导入、类型、参数、变量、条件、调用、返回和副作用逐行/语义段注释；追谁何时执行、值从何而来、状态改变、结果消费者与 UI 返回。你可按定位去看项目源码，但必要解释已在教材内。长链拆连续小课，不以职责表、类名箭头、未注释代码交差。详见 [教学协议](deep-codebase-learning/references/teaching.md) 与 [当前交付案例](docs/examples.md#l-v160-笔记优先与可选委派验收)。

**深度保留，叙事更连贯。** 新专业名词/缩写给准确全称、中文白话、解决的问题、当前用途及具体例子。沿一个业务场景，在首次影响理解的位置解释，再紧邻源码/例子推进；不堆长词典或百科。不要求你指出未知词，不设任意字数目标；范围太大拆课，不能为短删解释或为详细重复。

**官方资料读后讲进教材。** 核对相关依赖版本，实际读有帮助的章节，解释具体规则、框架/协议机制、对应项目语句、能确认和不能证明什么，再给直链/版本边界。读者不必自行搜文档补课。全文区分源码事实、官方规则、静态推断、真实观察和未知；至少一个具体输入串到可见结果，实际重要失败/取消等分支不遗漏也不虚构。

**默认单会话，首次可选委派。** 选择委派且宿主支持时，主会话规划每节目标/前置/范围，子 agent 写独占教材草稿，主会话逐段审查源码/资料映射并要求返修，合格后统一保存状态/索引。未选择或不支持则单会话；没有新工具、后台或模型限制。方法与所有权见 [编写模式](deep-codebase-learning/references/authoring.md)。

调查 investigated、草稿 prepared、正式教材 delivered、具体解释 explained、学习者证据 learner-evidence 分开。完整教材实际通读、补齐必要解释、V0/保存/索引后 delivered；single 可记 ready/self_review，真实独立审读范围可 validated，独审不是交付门票，不代表你已读或掌握。写出/阅读教材不会增加 mastery；合格内容可以交付，而 Stage 能力仍待验证。

| 环节 | 你获得的能力或记录 |
|---|---|
| 项目地图与动态路线 | 知道系统解决什么问题、实际有哪些模块、先学什么 |
| 纵向业务链 | 从用户动作或事件追实际输入、核心处理与返回消费者；有前端、API、存储则贯通 |
| 渐进源码讲解 | 看关键 Class/Method、数据与状态变化，理解 Why 和替代方案 |
| 知识绕行 | 发现必要基础缺口，补最小原理与例子，再回到源码 |
| 预测、实验、测验、复述 | 用独立表现证明能力，不把“懂了”当作掌握 |
| 横向审计 | 补齐 Config、Entity、DTO、异常、工具、测试、部署等重要遗漏 |
| 独立重建 | 先提出自己的设计，再实现可运行 Mini Version，与原项目比较 |

路线根据项目生成，不限 Java、Vue 或 AI/RAG。没有对应模块就不虚构。可持续阅读教材；要证明作者级能力仍需真实独立回答、实验与重建，Agent 不代答，能力等待不阻塞教材交付。

对话和笔记中的 Mermaid 图要求严格遵循对应图型的官方语法，输出前检查标签、ID、关键字、箭头与闭合；工具可用时实际解析/渲染。默认采用基础语法以降低旧渲染器兼容风险；未实测不会声称已渲染，已知 syntax error 必须先修复。详见 [图表协议](deep-codebase-learning/references/diagrams.md)。

## 记忆与笔记

```text
目标项目/.codelearn/
├── state.json       # 当前位置、待答题、返回点、下一动作
├── roadmap.md       # 动态路线
├── project-map.md   # 架构与业务地图
├── stages/          # 阶段目标与验收条件
├── coverage/        # Inventory、覆盖深度、源码有效性
├── mastery/         # 独立能力证据与复习日期
├── journal/         # 结构化认知变化，不是完整聊天记录
├── knowledge/       # 知识桥梁、问题与误解
├── notes/           # 中文阶段内容分类的完整教材、中文索引
└── reviews/         # 实验、测验、文章门禁与重建记录
```

有价值的交互自动保存，无需 `save progress`。Journal 记录学习过程；Notes 根据源码、问题、错误、实验及真实个人理解重新组织。

### 自动详细笔记与显式总结

每节直接写完整教材，固定会话也会持续保存，不等你要求总结：

| 时机 | 自动产物 |
|---|---|
| 本节一个因果目标形成完整、核对过的教学单元 | 中文阶段内容目录的详细小课，实际通读、必要修稿/V0、保存/索引后正式交付，不等测验或独审 |
| 多个相关主题积累到自然边界或上下文紧张 | 检查主题笔记已落盘，更新阅读索引、检查点与下一动作 |
| Topic/Stage 内容自然收束 | 整合主链与跨课关系，可先交付阶段文章；能力验收仍等待 |
| 阶段学习验收通过 | 更新综合文章与真实证据，能力/文章两门通过才标 Stage 完成 |

随时可以显式说：

```text
总结当前主题。
详细总结刚才的内容。
总结当前阶段。
总结当前会话。
重新核对这份笔记。
```

默认结构示例，具体分类随项目路线生成：

```text
.codelearn/notes/
  索引.md
  S00-项目全景/
    S00-T01-项目问题与业务能力.md
    S00-阶段总览.md
  S01-登录与权限/
    S01-T01-01-从输入到登录请求.md
    S01-T01-02-身份校验与页面返回.md
  会话/
  项目总览.md
  重建复盘.md
```

稳定 Stage/Topic ID 保留，中文名称反映教材内容；不把全部小课堆进 `主题/`。旧英文/主题目录在受影响范围迁移，更新索引、Stage、state、journal、review 和互链，不删历史或覆盖重名目标。每次交付前检查必要新词、真实注释源码、调用/状态、机制、例子/失败、已读官方资料、事实边界、独立可读性、叙事和路径一致性；不合格先补。详见 [教材通读要求](deep-codebase-learning/references/notes.md#note-quality-gate)。

**自动和显式笔记默认都作为待核对的候选内容。** `draft/ready/validated` 表达文章质量状态；`unverified/source_checked/runtime_checked` 表达实际核对及其范围。single 实际通读补缺后可 ready/self_review 正常交付；validated 留真实独立审读范围，两者均不证明实测或掌握，未运行实验和未知作者意图不会被写成事实。完整规则见 [使用指南](docs/usage.md) 和 [笔记协议](deep-codebase-learning/references/notes.md)。

返修先有可恢复旧版，局部补缺、保留正确必要解释，不能改成用途摘要。一次通读同时看语法/机制和正常/失败值链；自己懂不能补正文。仅广泛重写、源码范围大变或影响不明才全文重读，不另造逐段报表。精简重复动作，保留详细教学；未证明规则长短单独导致质量变化，也不保证更快。

v1.8.1 将每一跳写作落实到现有模板：必要背景、完整注释职责段、就近变量来源、逐句语法/值/Why、同值演算与真实下一消费者。调用方是否 await 必须看实际调用，JSX/分支不能丢定义或闭合。返修简记增改移删及保留去向，正文与当前修订记录同步，修旧课不覆盖当前学习位置；Skill 版本只按本轮实际加载记录。保留原有业务→架构→端到端→逐层源码顺序，不增固定章法或运行工具。

## 一小段示例

以下是教学示例，**不是实际学习成果或实验结果**：

```text
你：所以 Service 主要就是为了代码复用，对吧？
导师：复用可能是收益。先看当前 Service：它负责校验、保存消息，
      再调用供应商；Controller 负责 HTTP 适配。
      如果增加 CLI，哪些业务步骤仍适用？HTTP 错误映射放在哪里？
```

导师保存问题、纠正、未解误解及待答题；不会因为自己的解释就提高你的掌握度。更多 [示例与阶段门禁](docs/examples.md)。

## 使用边界

- 当前主要在 Codex 环境进行文件协议模拟；其他兼容 Agent 可试用，尚无同等行为验证。
- Agent 默认读取源码并更新 `.codelearn/`。改代码、安装依赖、运行有副作用的实验需要相应授权。
- 只在 Agent 被调用时执行；没有后台监听、定时提醒或跨文件原子事务。一个学习目录同时使用一个写入会话。
- 恢复时检查相关源码变化，失效证据需要重新验证；不会每轮全量读取仓库或全部历史。
- 私人源码和个人学习记录不应进入外部搜索或公开 Issue。是否提交或忽略目标项目的 `.codelearn/` 由你决定。
- 当前版本经过有界模拟和结构校验；大型项目规模、长期学习效果及全部异常恢复分支尚需真实试用。

## 仓库结构

可安装资源位于 [deep-codebase-learning/](deep-codebase-learning/SKILL.md)。根目录 README、`docs/`、校验脚本和 CI 为使用者及维护者服务，不需要随 Skill 安装。

```text
deep-codebase/
├── deep-codebase-learning/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── assets/templates/
├── docs/
├── scripts/validate.py
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## 参考与许可

教学与文档设计参考了 [learn-codebase](https://github.com/ktaletsk/learn-codebase)、[learning-codebases](https://github.com/Eijnewgnaw/learning-codebases)、[tutor](https://github.com/kevinnio/tutor)、[code-learn-skill](https://github.com/yumeiriowl/code-learn-skill) 和 [repo-learner-suite](https://github.com/PranitMohnot/repo-learner-suite)。具体采用与调整见 [设计来源](docs/inspirations.md)。没有安装这些项目作为依赖，也没有复制其代码或模板。

[MIT License](LICENSE)。问题与建议可提交到 [Issues](https://github.com/zgozh/deep-codebase/issues)。
