# Deep Codebase Learning

**在 AI 的长期引导下，学会解释、修改、定位问题，并独立重建一个真实项目的核心系统。**

[English](README.en.md) · [使用指南](docs/usage.md) · [设计与记忆](docs/design.md) · [验证与限制](docs/validation.md) · [贡献](CONTRIBUTING.md)

`deep-codebase-learning` 是一个 Agent Skill。它把学习组织成真实业务链，用源码和学习者的表现判断理解程度，并把进度保存在目标项目的 `.codelearn/` 中。换一个会话后，可以继续学习。

> Flow before files. Understanding before coverage. Evidence before mastery. Reconstruction before completion.

## 两分钟开始

需要一个支持 Agent Skills、能读取源码及写入本地文件的编码 Agent。Skill 运行不需要 Node、Python、数据库、MCP 或后台服务；下面的安装器需要 Node.js/npm。

用 [Skills CLI](https://github.com/vercel-labs/skills) 安装：

```bash
npx skills add zgozh/deep-codebase --skill deep-codebase-learning -g
```

只安装到 Codex，可加 `-a codex`；去掉 `-g` 则安装到当前项目。先查看、不安装：

```bash
npx skills add zgozh/deep-codebase --list
```

随后在要学习的源码项目打开新会话，说：

```text
带我深度学习这个项目。
```

以后在同一个项目的新会话说：

```text
继续学习。
```

如果没有自动选中 Skill，在 Codex 中显式说 `使用 $deep-codebase-learning 带我学习当前项目`。其他 Agent 的显式调用方式由其产品决定。手动复制安装和 Windows 步骤见 [使用指南](docs/usage.md)。

已配置GitHub SSH、但本机HTTPS访问不可用时，可将安装源替换为 `git@github.com:zgozh/deep-codebase.git`。也支持下载后从本地目录安装。

## 学习过程中会发生什么

| 环节 | 你获得的能力或记录 |
|---|---|
| 项目地图与动态路线 | 知道系统解决什么问题、实际有哪些模块、先学什么 |
| 纵向业务链 | 从用户动作或事件，追到前端、API、后端、存储及返回结果 |
| 渐进源码讲解 | 看关键 Class/Method、数据与状态变化，理解 Why 和替代方案 |
| 知识绕行 | 发现必要基础缺口，补最小原理与例子，再回到源码 |
| 预测、实验、测验、复述 | 用独立表现证明能力，不把“懂了”当作掌握 |
| 横向审计 | 补齐 Config、Entity、DTO、异常、工具、测试、部署等重要遗漏 |
| 独立重建 | 先提出自己的设计，再实现可运行 Mini Version，与原项目比较 |

路线根据项目生成，不限 Java、Vue 或 AI/RAG 项目。没有前端、MQ、AI 或数据库就不虚构相应课程。学习者需要回答、尝试和验证；Agent 不会替你回答测验。

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
├── notes/           # 重新编写的正式技术文章
└── reviews/         # 实验、测验、文章门禁与重建记录
```

有价值的交互自动保存，无需 `save progress`。Journal 记录学习过程；Notes 根据源码、问题、错误、实验及真实个人理解重新组织。阶段必须同时通过学习验收和文章质量检查，才会推进。

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
