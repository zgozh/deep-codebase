# 设计与长期记忆

[返回 README](../README.md) · [权威记忆协议](../deep-codebase-learning/references/memory.md)

## 三个独立成果

Project Coverage 追踪项目区域学到什么深度；Knowledge Mastery 追踪学习者的独立能力；Reconstruction Ability 追踪脱离原源码能重新设计和实现什么。三个维度不能合成“看了多少文件就懂了多少”。

coverage 的六种深度是 discovered / seen / explained / traced / understood / verified；mastery L0–L6 是 Unknown / Seen / Recognized / Explained / Applied / Verified / Reconstructed。重要度决定目标，不要求逐行讲解全部 trivial helper。

## 教学规划

先建立架构地图与业务地图，再选代表性功能追 Vertical Slice。重要 DTO、配置、异常和基础原理在实际链中触发；主要链完成后 Horizontal Audit 补未进入主链的结构。

Roadmap 使用稳定 Stage ID，允许根据新模块、知识缺口和错序修订。每阶段有能力目标、实际源码范围、动态 Exit Criteria、实验与评审要求。自动化管理不会替学习者作答。

```mermaid
flowchart TD
    A[识别项目与局部恢复] --> B[地图和动态路线]
    B --> C[一个业务链教学单元]
    C --> D{是否有阻塞知识缺口}
    D -- 有 --> E[知识绕行与独立检测]
    E --> C
    D -- 无 --> F[预测 / 实验 / 测验 / 复述]
    F --> G[提取事件并持久化]
    G --> H{阶段学习门禁}
    H -- 未通过 --> C
    H -- 通过 --> I[重写文章与质量门禁]
    I --> J[下一阶段或横向审计]
    J --> K[独立设计与可运行 Mini Version]
    K --> L[项目综合验收]
```

图是能力闭环概览，不强制每次交互经过全部节点；每轮有意义交互都保存。详细 [教学](../deep-codebase-learning/references/teaching.md)、[评估](../deep-codebase-learning/references/evaluation.md)、[笔记](../deep-codebase-learning/references/notes.md) 是 Agent 执行协议。

## Schema v1 的职责

| 文件/目录 | 唯一主要职责 |
|---|---|
| state.json | 恢复入口、当前Stage/Topic、awaiting、返回栈、next_action、提交指针 |
| roadmap.md / stages | 学习顺序、依赖、每阶段能力合同 |
| project-map.md | 系统边界、模块关系、业务入口与运行拓扑 |
| coverage | 分模块Inventory及达到目标所需的证据 |
| mastery | 分领域规范概念记录、能力证据、误解、复习日期 |
| journal | 分Stage分片的认知增量与提交恢复信息 |
| knowledge | 知识桥梁、个人问题和深度边界 |
| notes | 重建后的独立技术知识文章 |
| reviews | 测验、实验、阶段/文章门禁、审计、重建与恢复证据 |

模板默认 null/空列表是尚无事实。概念记录见 [concept.json](../deep-codebase-learning/assets/templates/concept.json)，其 target 只是待调整起点；没有真实回答不能填入假证据。日期字段是 ISO 日期或 null，待回答的即时动作写 next_action。

机器记录中的学习路径相对项目根；Markdown链接相对所在文档。写记忆只在当前 `.codelearn/` 内，先检查解析后的路径及软链接边界。root_hint 不能指挥恢复器去任意旧目录。

## Journal、Notes 与个人认知

Conversation 是临时交互。Journal 记录问题、当时理解、纠正、提示程度、预测/观察、未解项及能力变化。Notes 将源码、这些记录和真实用户表述重新编排成技术文章，不是事件列表或聊天摘要。

阶段完成有两道门：学习能力通过，再检查文章能否仅凭源码和 `.codelearn/` 独立读懂。文章缺个人证据时返回教学；不能让AI润色出一段“我的复述”冒充用户回答。

## 文件提交与恢复

POST-TURN 依次 CLASSIFY → EXTRACT → EVALUATE → PERSIST → CHECKPOINT → STAGE CHECK → PLAN。写 pending 事件及 state 指针后更新必要记录，校验后提交事件，最后更新 state 并清 pending。

这是可审查的文件协议，**不是数据库事务，也不是 Git commit**。恢复时使用 event ID 和条目 ID 补未完成写入，避免重复证据。冲突保留并报告，不覆盖后来用户改动。无锁/多人合并能力，因此同一目录只用一个写者。

## 上下文与源码变化

恢复通常只读取state、当前路线/阶段、近期3–5个事件及相关mastery/coverage/knowledge/review。Journal分片；大型Inventory分模块；文章分节检索证据。不能用减少context为理由猜测源码。

Git branch/HEAD、dirty/untracked和相关文件指纹都影响有效性。非Git项目使用实际hash。相关变化只重开受影响的证据与门禁，保留历史能力和通用知识。

## 产品边界

v1由Skill指令与学习文件组成，无服务、MCP、向量库或运行脚本。根目录 `scripts/validate.py` 只供维护者校验发布文件，不参与学习。没有后台任务、自动到时提醒、绝对原子写入或已证明的长期效果承诺。
