# 证据、覆盖与完成

## Mastery L0–L6

| Level | 最少证据 | 不能用来代替的东西 |
|---|---|---|
| 0 Unknown | 尚无能力证据/确认无法识别 | 未讲不等于不会，背景自述只作线索 |
| 1 Seen | 教学/检查中过该概念，有出处 | AI讲过不代表独立理解 |
| 2 Recognized | 用户在新例子正确识别职责/概念 | 点头/复读题干 |
| 3 Explained | 用户用自己语言解释机制、位置、因果 | 复制 Notes 或高提示下背答案 |
| 4 Applied | 独立预测新情境、诊断或判断改动影响 | 同一道题的纠正后答案 |
| 5 Verified | 用户预测/尝试并经真实实验/修改/调试验证，再解释观察 | AI运行成功、静态推演或“我跑了” |
| 6 Reconstructed | 用户少依赖源码独立设计/实现核心机制并验证 | AI代写的 Mini Version 或架构图 |

使用 [mastery 文件模板](../assets/templates/mastery.json)，每个 concepts 条目由 [concept 模板](../assets/templates/concept.json) 填充。记录 concept_id、level、target、evidence、misconceptions、gaps、last_checked、source_valid 与 review_due。跨 Stage 的共享概念只有一个 owner 文件，其余引用该 ID。

`level`/`target` 为 0–6 的整数；concept_id 填稳定 ID，模板默认 target=4 只是起点，按 Stage 能力目标调整。每份 evidence 至少有 event_id、可选 review_ref、independence（independent/hinted/tutor-provided）、hint_count、prompt、answer（未答为 null）、evaluation、source_refs。gap/misconception 条目用 id/status/event_id 关联，状态保留 suspected/confirmed/resolved 或 unresolved 的实际含义。last_checked/review_due 用 `YYYY-MM-DD` 或 null；等待本题回答等即时动作写 state.next_action，不把自然语言塞进日期字段。

演示、模拟学习者或人为 seeded 的实验/回答必须在独立测试目录标明 provenance；只能验证教学协议，不能进入真实学习目录的 mastery/coverage 或用作 Stage/Project 通过证据。示例文章写得再详细也不证明真实学习者理解或真实实验运行。

判断 Correct / Partial / Incorrect / Misconception，说明具体因果。将有提示的表现与独立表现分开；重新举例后独立通过才能升档。错误不是一律清零：失误保留历史证据，关键机制的确认误解可降至当前证据支持的 level，记录旧→新与原因。先等待纠正后的回答，不能因 AI纠正就清除误解或提高掌握度。

复习是调用时的队列，无后台定时器。独立回忆通过可依次约 1/3/7/14/30 天复查；失败缩短间隔并安排补救。只是识别不足以证明旧 L4/L5 全部恢复。复习优先本阶段依赖与未解误解，不一次问完所有到期题。

## Coverage 六种深度

| 状态 | 意义与最低证据 |
|---|---|
| discovered | 已枚举并定位，职责尚未确认 |
| seen | 相关源码实际打开/检查过 |
| explained | 源码支持的职责/机制解释已记录 |
| traced | 在真实链路内确认调用、数据/状态与错误路径；非调用型配置追消费者/加载链，文档追实际约束 |
| understood | 学习者独立解释该机制并预测合理影响（一般至少相关 L3，Critical 至少 L4） |
| verified | 真实实验/修改/调试与学习者解释支撑（一般相关 L5） |

`depth` 存最高已支持深度，evidence 保留具体已达到的维度；运行过不自动填满 understood，读过不自动 traced。每个条目设 target_depth / target_mastery，重要度默认：Critical understood+Applied，并为高风险/关键行为指定 required verification；Important understood+Explained，涉及行为变更通常 Applied；Normal explained；Trivial discovered 加职责确认即可。特定 Stage 可提高目标，不为 100% 对所有 helper 深挖。

分面板报告：关键链路已达目标数、各模块/类型/重要度 coverage、独立能力分布、重建机制通过数。若展示加权比例，可用 Critical/Important/Normal/Trivial = 4/2/1/0.25，分子为达到该条目目标且有效的权重；同时报告枚举范围与 pending，不能把它称总体理解百分比。禁止“看过 100% 文件所以懂了 100%”。

## Quiz、Restate 与 Stage Exit

Stage 开始就定义动态验收；从 source-backed 场景混合识别、因果、预测、诊断、改动影响、设计取舍题。一次一问，未答为 waiting。保存真实题目、用户回答要点、提示、评价、支撑能力与未解问题。题目答案不能在问前泄露；学习者有合理替代答案时修正 rubric，不强制原设计是唯一正确方案。

Restate 要学习者自己讲出起点、各层职责、关键数据/状态转换、结果/错误返回及一个设计理由。允许简短，不代替他们编写“我的复述”。未取得时写 waiting 或未验证，而不是补一段 AI文章假装用户讲过。

逐条检查 Stage criteria：关键 Topic/Source Path 到目标、必要原理的独立表现、无阻塞 gap/误解、综合 Quiz/Restate、required experiment、分区 coverage audit、source_valid。证据 ID 链接实际记录；optional 未做与 N/A 不伪装通过，required blocked 就保持 in_progress。

重要 Topic 讲解收束即按 [Notes 协议](notes.md) 写详细主题文章；显式总结也可提前写 Stage 草稿，缺失的能力/实验仍 waiting，phase/awaiting 保留，不能因有笔记就完成阶段。学习门禁通过后才进入 STAGE_SUMMARY，综合并审计 Stage 文章。质量门禁通过且关键事实实际核对、无关键 stale 证据，再写阶段 review、状态 complete 并自动安排下一个合适动作。文章的 validated 是质量状态，不是独立验证或能力证据。正常教学到需要用户新回答时结束本轮；自主推进不意味着代答全部测验。

## Reconstruction

先 Horizontal Audit 和整体 Architecture Review，关闭 Critical/Important 漏项。学习者先在尽量不看原源码/Notes 的条件下提出设计；记录查阅程度，合理画图/伪码阶段不等于已实现。

按项目真实范围重建模块、数据模型、API/核心 Interface、业务链、存储/缓存、异常/配置、前端/部署，以及存在的 AI/RAG/Agent/MCP 等。评估能否解释职责、关键失效模式、改动影响、替代方案；先冻结用户方案，再对照 Original Design，按场景讨论相同/不同/Why/trade-off，允许用户方案更合适。

与学习者选一个代表核心机制的 Mini Version 范围，必须由学习者承担关键设计与实现。最小可运行纵向链包含输入→核心处理/状态→输出；有前端原项目应重建相应用户界面/状态/API 边界，有异步/流式关键机制则保留其行为。允许离线 stub 外部供应商，但需明确未证明的机制并以可运行替代实验补证。

在隔离目录实现，保护目标源码；AI提供最小必要提示/评审，不悄悄写完关键机制。验证正常路径和代表性错误/影响场景。保存实际产物定位、运行证据、用户解释、帮助程度、与原设计比较及尚未实现范围于 reconstruction review。无法运行只能记 design_reconstructed/implementation_pending，不能宣布最终完成。

## Project Complete 的必要条件

1. 所有 Critical feature/architecture 路径有效且达到目标，全部枚举范围明确。
2. Important 横向组件无遗漏；合理 trivial 排除有理由，所有 pending 分区已审计。
3. 关键知识达到预定独立能力，无阻塞 gap/误解或关键 source revalidation。
4. required experiments 实际完成、Stages/reviews/Notes 通过各自门禁。
5. 学习者可脱离源码解释/定位/预测主要影响，并完成独立设计与可运行 Mini Version。
6. 最终 [Deep Dive 与 Reconstruction Review](notes.md) 写入并过质量门禁。

否则只报告当前能力、未完成条件、下一动作；不能因课程全讲过或用户说“结束吧”伪造 PROJECT_COMPLETE。用户结束本次会话只做 session checkpoint。完成后保留复习/源码变化入口，不再自动创建无关课程。
