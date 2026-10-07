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
