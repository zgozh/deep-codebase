# 设计与长期记忆

[返回 README](../README.md) · [权威记忆协议](../deep-codebase-learning/references/memory.md)

## 教学内容、交付和能力

Project Coverage 跟踪实际区域与机制覆盖深度，Knowledge Mastery 跟踪真实学习者能力，Reconstruction Ability 跟踪脱离源码可重建的系统。文件数、教材篇数和用户说“懂了”不能替代任何能力证据。

v1.8.0 默认正式交付是详细独立笔记，不再是聊天课堂后的重组。聊天简短给实际范围与链接、随时充分答疑；仅明确整课聊天请求才展全文。所有渠道共用 [详细内容合同](../deep-codebase-learning/references/teaching.md#唯一教学交付合同)，局部答疑按问题范围，不能要求源码/官方资料/聊天补齐当前必要解释。

初学者默认：只提过名称、贴过源码或概述职责不算机制已解释。新概念在首次影响理解处给全称/白话/当前用途/例子，源码和解释紧邻，按具体业务场景及真实调用顺序展开。小课限制因果目标广度，不限制必要解释深度，不设字数目标；当前语言/框架前置先于依赖代码，范围大则拆连续中文小课。

路线仍从问题→能力→架构→代表端到端功能→源码机制开始；垂直业务触发重要配置/对象/异常等，横向审计补未进入主链的重要结构，最后独立重建。依项目生成完整路线，不机械套固定栈。每阶段定义 exit criteria，内容教材可交付而能力仍 waiting，不能用“文章完成”批准 Stage/Project 完成。

## 两种编写方式

默认单会话；首次提供一次主会话规划审查、子 agent 编写选择，未答继续默认，有选择则存当前合同与 journal 跨阶段恢复。无需子 agent 也可学习，不固定模型/档位、不增运行工具，宿主和用户限制优先。

委派是编写责任拆分，不是让子 agent 自己规划或写共享进度：主会话给有界目标/前置/真实源范围与唯一稿路径，子 agent 实读源码和官方资料写稿，主会话在独立上下文逐段核对并要求返修。仅主会话写索引/state/journal/mastery/coverage；不得并行编辑同稿。真实 author/reviewer 和检查范围进入 review，不能从子 agent 自报通过推断合格。失败时明确交还稿件所有权并可单会话接手，恢复无需旧子会话继续存在。见 [编写协议](../deep-codebase-learning/references/authoring.md)。

## 单轮工作流与正式教材门禁

恢复偏好与实际教材边界 → 选问题/主链，读真实源码和必要官方资料 → 尽早写一份完整可读稿 → 一次实际通读、补正文缺口 → 必要 V0/保存与真实学习变化 → 简短主题/范围/链接。single 自查可交付，delegated 主会话独立读子稿。讨论/中断仍及时 checkpoint，未变已读资料和检查证据复用。

官方资料要讲具体规则、机制、源码映射、能证明与不能证明什么，再直链和版本边界。源码事实、规则、静态推断、真实观察、假设例子与未知明确区分；私人源码/记录不上传外部服务。必要解释缺失先补，不把 unknown 当合格借口；实际未运行可明确静态范围。

[教学合同](../deep-codebase-learning/references/teaching.md#唯一教学交付合同) 规定详细语法/机制/场景/Why、真实源段与正常/失败值链；[作者流程](../deep-codebase-learning/references/authoring.md) 唯一维护写读返修。移除强制独审门票、分门报表、教材双 hash 与固定元数据布局。single 完整稿通读补缺后可 ready/self_review 并 delivered，validated 用于实际独立审读范围。简记方法/范围、重要出处和缺口处理，自己懂或能重放值链不替代必要解释。

返修先有一份可恢复旧版，局部修并对照正确必要教学单元保留，迁移目的已写好/入口有效/本节必需含义仍在。源码 revision 与 dirty 相关文件指纹用于可靠来源核对，不作为教材质量证明；仅广泛重写、源码范围大变或影响不明才全文重读。历史 validated 不批量洗白，教材完整不替代阶段/项目能力证据。

## Schema v1 的职责

| 文件/目录 | 主要职责 |
|---|---|
| state.json | 恢复入口、当前 Stage/Topic、返回点/待答、next_action、提交指针 |
| roadmap.md / stages | 动态路线、必要前置、真实交付范围、偏好/编写模式及能力合同 |
| project-map.md | 系统边界、业务入口、模块依赖和运行拓扑，不代替教材 |
| coverage | Inventory、discovered/seen/explained/traced/understood/verified 及对应实际证据 |
| mastery | L0–L6 的真实学习者表现、误解、复习与有效性；模型交付不升级 |
| journal | 结构化认知增量、备课/交付/能力范围、写入恢复信息，不是 transcript |
| knowledge | 当前必要知识桥梁、解释深度/来源与返回点，不造全仓词典 |
| notes/索引.md | 按阶段分组的中文教材入口、稳定 ID、范围/事件、质量/核对与接续 |
| notes/Stage ID-中文内容 | 每节中文详细教材、阶段综合；按实际内容分类，不堆统一主题目录 |
| notes/会话、项目总览、重建复盘 | 会话实际范围与最终系统综合/独立设计比较 |
| reviews | 测验/实验/文章与阶段门禁、审计、重建、恢复的实际证据 |

state 字段与 schema_version=1 保持，编写模式/是否询问存合同和 journal，无必填 JSON 扩展。模板空值不是能力证据。概念规范见 [concept.json](../deep-codebase-learning/assets/templates/concept.json)。机器路径相对项目根，Markdown 相对所在文档；写入限当前 `.codelearn/`，先核实路径和软链接边界。

中文阶段内容路径可按触及范围迁移旧主题/英文结构；保留稳定 ID、旧→新映射和历史能力，所有关联索引/Stage/state/journal/review/knowledge/roadmap/互链一起更新。冲突或占用不覆盖/强删，不为恢复全量迁移历史。

## 解释深度与学习者证据

investigated 是调查，prepared 是草稿/拟发解释，delivered 是完整教材实际通读补缺、必要 V0/保存/索引成功；single 可 ready/self_review，未完整稿仍 prepared；explained 指实际充分解释的教材段落/可见聊天及深度；learner-evidence 是实际用户回答/预测/实验/实现。文件 pending/committed 只是写入，不是教学或能力状态；正式交付不证明用户读过。

写出/阅读文章和导师讲解不会增加任何 mastery level，包括 L1。Coverage 的 explained 可以由源码支持的合格教材解释支撑，understood/verified 仍需用户表现与运行证据。提示程度与独立性分开，用户自述读懂不等于独立理解。教材可 validated，而阶段所需实验/restatement 仍 waiting；不存在伪造用户回答才能交付的要求。

个人问题、原理解、纠正和 Aha 只写真实历史，不能把 AI 的设计/润色当独立用户方案。笔记质量 draft/ready/validated 与事实核对 unverified/source_checked/runtime_checked/needs_revalidation 独立记录，既有笔记缺 verification 保守使用，当前修订补字段，不批量清零。

## 文件提交与中断恢复

POST-TURN：CLASSIFY → EXTRACT → EVALUATE → PERSIST → CHECKPOINT → STAGE CHECK → PLAN。pending 事件与 state 指针后更新必要内容/索引，校验才 committed，最后更新 state 指针并清 pending。它不是 Git commit 或数据库事务。

用稳定 event/条目 ID 补未完成写入，不能重复能力证据；冲突保留报告，不覆盖用户后来改动。共享状态唯一主写者，草稿作者仅拥有指定文件，无并发事务能力。无法保存如实报告并保留恢复记录，停止依赖成功保存的跨 Topic 推进，独立答疑可继续。

## 上下文、源码变化与边界

恢复只读 state、当前合同/路线、笔记索引/相关前课段落、近期 3–5 个事件及相关能力/知识/coverage/review。大文档搜 ID/标题读相关段；每节顺因果链加载必要源码，证据不足再扩大，不全量读历史/仓库，也不能以省 context 猜测。

Git branch/HEAD、dirty/untracked 与相关文件 hash 影响有效性，非 Git 用实际指纹。仅受影响链路/笔记/门禁 needs_revalidation，能力历史与通用知识保留；关键契约变化重开相关 Stage/项目验收。

产品只有 Skill + `.codelearn/`，无后台/服务/MCP/复杂 CLI。根目录 [校验脚本](../scripts/validate.py) 只供发布维护，不参与教学。真实模型遵守、长期效果和所有项目成功都须额外实践证据，不能从规范或结构检查保证。
