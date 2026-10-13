# 持久记忆与恢复协议

索引关键词：Schema、PRE-TURN、POST-TURN、pending、源码变化、上下文预算。

## Schema v1

```text
.codelearn/
  state.json                 唯一恢复入口与最近提交指针
  roadmap.md                 稳定 Stage ID、顺序、依赖与文件索引
  project-map.md             架构/业务双地图与证据
  stages/<stage-id>.md       当前教学合同、Topic 与 Exit Criteria
  coverage/index.md          模块分片、扫描范围、遗漏/有效性概览
  coverage/<module>.md       Inventory + 覆盖证据，必要时再分片
  mastery/index.md           概念领域、文件、复习/缺口路由
  mastery/<domain>.json      每个概念一个规范记录
  journal/<stage-id>-001.md  事件分片，append 优先
  knowledge/index.md         当前概念/桥梁/误解/问题的轻量路由
  knowledge/<topic-id>.md    知识桥梁与个人理解
  notes/索引.md              按阶段分组的教材入口、事件边界、质量/核对状态
  notes/<Stage ID>-<阶段中文内容>/<稳定课ID>-<中文目标>.md  每节正式教材
  notes/<Stage ID>-<阶段中文内容>/<Stage ID>-阶段总览.md   阶段综合
  notes/会话/<session-id>-学习回顾.md  按真实事件范围整理
  notes/项目总览.md          完成后的总知识地图与跨模块综合
  notes/重建复盘.md          独立设计与原系统的比较及验证
  reviews/<review-id>.md     Quiz/实验/阶段评审/审计/重建证据
```

只创建已用到的文件；首轮至少 state、roadmap、project-map、当前 stage、三个 index 及当前分片。空列表表示尚无证据，不生成不存在的模块。使用 [state](../assets/templates/state.json)、[mastery](../assets/templates/mastery.json)、[coverage](../assets/templates/coverage.md)、[journal](../assets/templates/journal.md) 模板。

所有文本使用 UTF-8。Windows PowerShell 读取中文必须显式 `Get-Content -Encoding UTF8`，写入用明确 UTF-8 的文件工具；不要依赖系统默认编码。给 Windows PowerShell 5.1 执行的含非 ASCII 脚本用 UTF-8 BOM 或不含非 ASCII 的脚本内容，避免模板/日志乱码被误当成学习状态损坏。

state 的必需字段：`schema_version`、`skill_version`、`project`（name、root_hint、revision、identity_sources）、`learner`（背景已知/未知、目标、语言）、`mode`、`phase`、`current`（stage/topic/source_refs）、`return_points`、`awaiting`、`next_action`、`focus_files`、`journal`（active_file/last_event/next_sequence）、`open_loops`、`pending_commit`、`updated_at`。

初始化时按实际用户语言和目标填写 learner，未知背景保持 unknown；`learner.teaching_default=beginner` 表示教学策略，不是用户能力事实。旧 schema v1 没有该可选字段也按 beginner 教学，当前更新 state 时可补入，不重置历史。模板文本不构成用户能力证据，也不锁定教学语言。日期使用 ISO 8601，未发生的时间用 null，不虚构历史。

- 路径相对项目根；root_hint 只帮助发现迁移，不能作为唯一身份或失效依据。模块/Stage/Concept/Event ID 稳定且全项目唯一。迁移目录时优先根据源码身份与布局判断，不盲写旧绝对路径。
- state/focus_files/journal/rubric/next_action 中的学习记忆路径统一相对项目根，如 `.codelearn/stages/S01.md`；Markdown点击链接则相对所在文档。读取或恢复写入前解析路径，记忆写入必须位于当前项目 `.codelearn/`，不得跟随逃出该目录的软链接；source_refs 位于当前项目内。超范围路径作为未知/冲突处理，不自动访问。
- `revision` 存 git branch/commit（无 Git 可 null）及相关源码内容指纹。SHA256 用宿主工具计算，不自行生成假的 hash。每个 source_ref 至少 path、symbol（可空）、revision/hash、evidence_kind。相同版本共享 revision，已 dirty 或非 Git 源文件保存内容 hash。
- `awaiting` 为 null 或 `{kind, prompt, topic, source_refs, issued_event, rubric_ref}`；仅保存通过教学就绪检查、适合当前目标的待答题。不是每轮必填，无题时 null。评分标准放 reviews 文件按需读；尚未回答不能当失败或通过，用户要求先讲解时原题移到 journal/阶段待复习项而非继续占住当前 awaiting。
- `next_action` 存 type、target、reason、load（必要路径）、completion_condition，不能只是“继续”。`focus_files` 仅当前 stage/当前 mastery 与 coverage 分片/当前知识记录/相关 review。
- `open_loops` 只放当前阻塞/误解/未解题/复习的 ID 与路径；其他历史通过 index 查找，不把所有问题复制到 state。
- schema_version 未知时只读并报告需要兼容，保留文件；v1 不猜测升级或重置历史。

三个 index 都采用简单 Markdown 表格：ID/区域、文件、当前重点/有效性、扫描状态或下次复习时间。索引保存路由和概览，详细真相在分片；变更后只更新相关行。

## 教学状态机

`phase` 表示当前下一教学动作，不是线程或后台任务；waiting 由 awaiting 表达，用户提问可从任意教学状态跳转。只写实际发生/等待的状态。

| 状态 | 进入/退出规则 |
|---|---|
| INIT → PROJECT_SCAN → ROADMAP_BUILD | 识别项目、建立 Inventory/双地图、保存动态路线；首课可在分区仍 pending 时开始 |
| STAGE_START → TEACH | 当前合同/目标/Exit Criteria 已建立，选择一个 Topic |
| INSPECT_CODE / TRACE | 读实际源码、验证当前调用/数据链，回 TEACH 或 PREDICT |
| KNOWLEDGE_DETOUR | confirmed blocking gap；保存返回栈，补知并检测后返回原位置 |
| PREDICT → EXPERIMENT | 等用户预测；实际授权与环境具备才运行，否则记录 blocked |
| QUIZ / RESTATE → MASTERY_CHECK | 等真实回答后评价独立证据，不能跳过等待 |
| REMEDIAL | exit criterion 未通过或关键误解；缩小问题、补知或新场景再评估 |
| STAGE_SUMMARY | 学习 exit criteria 通过；写文章并过质量门禁，失败修订或回补救；两门均过才 Stage complete |
| HORIZONTAL_AUDIT | 主链完成；发现遗漏回 STAGE_START 补学，再复查 |
| RECONSTRUCTION | 全系统覆盖有效；独立设计、实现 Mini Version、验证、原设计比较 |
| PROJECT_COMPLETE | 所有完成门禁通过且总文章有效；相关源码变化时重开 affected Stage |

Session checkpoint 保留位置，不增加用户操作。课程教材交付与能力验收分开：阶段需要用户新证据时验收 waiting，仍可继续合理后续课程并保持原阶段 in_progress。不能扮演学习者或以测验阻止读教材。编写模式按 [authoring](authoring.md) 首次询问、默认 single，选择/是否已询问存当前 stage 与 journal，切阶段继承，不新增必填字段。

## Journal 与事件

每个 meaningful interaction 提取一个或少量事件，用稳定 `E000001` 连号。事件按模板保存：类型（question/answer/reasoning/misconception/gap/insight/aha/source_discovery/prediction/experiment/quiz/restatement/mastery_change/coverage_change/design_decision/unresolved/teaching/checkpoint 等可组合）、Stage/Topic、source_refs、用户原理解或简短原话、纠正与依据、独立证据/提示、认知变化、未解项、下一动作。

完整 transcript 禁止。保留关键问题、关键个人表述和实验结果；AI长讲解提炼成可重建的机制/链路/出处，不能只写“讲了 SSE”。涉及敏感值用占位符。Aha 是用户实际表达的领悟，不能替用户杜撰。

Journal/阶段检查点按下节记录实际概念解释深度与可见依据；语义摘要不等于完整聊天副本。只提名称、贴代码或概述职责不算工作机制已教，不能批准依赖该机制的复杂题目。

事件额外有 `status: pending|committed`、`writes` 与必要 `deltas`：记录受影响文件/条目、旧值→新值及足够恢复的内容。writes 是路径清单，不复制整篇 Notes。写出/读过教材、模型讲解不支持 mastery 升档，包括 L0→L1；按实际学习者证据评估各级，一个 answer 不意味着其他概念都提升。

每片约 100 个事件或 32 KiB 开新片，不删除历史。只读近期尾部及相关 ID，可 rg 搜历史。每节详细教材按 [笔记协议](notes.md) 写入中文阶段目录，notes/索引.md 保存稳定 ID、路径、实际起止范围、事件/最后整理事件、quality/verification、未解及下一节。会话总结按真实事件边界：首次 checkpoint 记 session ID/首事件，缺记录则明确可恢复范围，不猜历史。元信息存 journal/索引，不迁移 state schema。

## 讲授范围与概念语义记录

保持 schema v1 与现有目录，在 journal 与当前 stage 用可读条目分别记录：

| 范围 | 可支持的结论 |
|---|---|
| investigated | 导师查过哪些源码、版本与资料；不代表已教 |
| prepared | 调查后的拟交付解释/草稿及范围，未通过交付门禁；不是正式教材 |
| delivered | 笔记已保存、回读、内容门禁/V0通过、登记索引，可供阅读；记录路径、版本、事件与 review，不证明用户已读 |
| explained | 具体充分解释的范围/深度：已交付笔记段落，或实际可见聊天消息；记出处，不是能力 |
| learner-evidence | 实际回答/预测/实现/实验及 independent/hinted/tutor-provided；能力单独评估 |

这些是语义范围，不是 mastery 等级或文件事务状态。pending/committed 只是写入过程，文件存在不保证合格。已通过内容/V0并保存、回读、索引的笔记能确认 delivered 与具体解释范围；不能推断阅读/掌握，未展开内部不能算已解释。聊天拟发内容仍 prepared，只有实际可见消息才确认 explained，不假定发送回调。旧版“explained 只能由聊天证明”不再适用笔记正式交付；旧 prepared 文档须回读核对再交付，不能批量升级。

恢复交付中断时核对实际笔记/索引/review/事件，满足条件才确认 delivered；缺失就 prepared 并补稿，不声称已发聊天链接。旧泛称“讲过”按当前触及概念补深度，保留稳定 ID 和真实能力历史，不全量批改。中文阶段分类迁移按笔记协议映射并检查所有相关引用。

knowledge/index 只路由当前有用概念到 `knowledge/<topic-id>.md`，多个相关条目可共用文件，不为每个标点建档。简记 Concept ID、白话/当前用途、实际解释深度/仍缺部分、例子或混淆、正式教材段落/可见聊天/官方章节/源码/事件与返回点。详细正文指向中文阶段教材，不复制整篇；无正式交付/实际可见依据的解释留 prepared，不造全项目占位词典。学习者能力另记。

最新详细度/逐句/官方文档偏好写 journal 并在当前 stage 保留可恢复摘要，持续应用后续课。切换 Stage 前，将仍生效的偏好与来源事件复制到新 stage 教学合同，并更新 roadmap 当前行的合同路径，让恢复入口始终指向含偏好的当前合同；不能依赖近期 3–5 条 journal 恰好包含旧偏好。教师遗漏列有限修复项，不标为学习者失败。无需新增必填 state 字段或运行脚本。

## PRE-TURN LOAD

每次新会话/“继续学习”执行完整协议；同会话继续时复用已加载协议和未变状态，只读必要变更。

1. 查 `.codelearn/state.json`。不存在时检查残留目录和其他学习记忆，避免覆盖；真正全新才初始化。目录存在却 state 丢失则从 roadmap、阶段合同与最近 committed 事件重建保守检查点，不能当新学习者抹掉成果。
2. 核对 schema/项目身份、恢复 pending。读当前 roadmap/stage 的最新交付偏好、编写模式及已交付范围、相关 mastery/coverage/knowledge/review、中文笔记索引与本节必需前课段落；近期 journal 默认 3–5 个有价值事件，必要时向当前合同查较早持久偏好。不读全历史，不把 prepared 当 delivered 或把 delivered 当掌握。
3. 检查源码变化（后文）。相关失效先重新定位，不能沿过期方法继续教学。
4. **最新意图/反馈优先于旧 awaiting/next_action/历史偏好**。当前默认笔记优先，已明确的最新交付调整不得被旧“聊天是课堂”覆盖。核对真实已交付范围/必要前置，找返回点、误解和未解。用户要求先讲或拒绝测验暂停题目并保留待评估，不记失败；有 Note 不证明其读过，也不足以强制考试。Recall 只在内容确有解释依据、适合当前目标且用户愿意时安排，不机械重考。
5. 按当前阶段实际编写下一节或修补当前缺失，默认简短给范围与笔记链接；提问直接答疑，明确完整聊天课堂才展开整课。不只报恢复或下一文件列表。旧题非读笔记门票，能力验收可 waiting 而教材继续；只有必要记录确实缺失才请用户补充。

上下文初始预算通常 5–8 个短文件/局部段落，state 尽量 <8 KiB。大文件搜 ID/标题再读相关段；源码从当前符号及必要依赖开始，证据不足再扩大。每节教材按因果步骤逐段读取与写作，不一次加载全部历史/源码；省 context 不能猜测。

## POST-TURN LEARNING COMMIT

每轮交付前先过 [单轮自检](teaching.md#发送前单轮交付自检)，笔记还过质量/V0，再在响应结束及换 Topic 前提交。prepared 草稿与正式 delivered 分开，只有充分解释及来源可支持 explained 覆盖，职责表/类名箭头不够；任何交付/阅读不提升 mastery。未合格保留调查/待写点，已有真实证据不回退；有价值变化自动保存，单纯问候不造事件。

1. **CLASSIFY**：判定有哪些学习事件，回答是否 independent/hinted/tutor-provided。
2. **EXTRACT**：提取新事实、出处、用户理解、错误/纠正、问题、预测、实际结果；不要捏造未运行观察。
3. **EVALUATE**：按真实证据评估 mastery/coverage、gap/misconception、源码有效性。正式笔记只支持实际充分解释/追踪范围；没有学习者表现，不增加 mastery，包括 L1。用户说读过或懂不等于独立理解。
4. **PERSIST**：先追加 pending 事件/writes/deltas，再写 state.pending_commit；由唯一主会话更新必要 coverage/mastery/knowledge/review/stage/roadmap、教材与中文索引。回读、检查 JSON/本地路径/锚点及 ID 对应实际符号，核对质量与源码版本，合格教材记 delivered/解释深度。不合格稿仍 prepared。事件改 committed；最后更新 state 指针/current/awaiting/next_action 并清 pending。无题 awaiting=null，写出/可读不代表用户已读或掌握。
5. **CHECKPOINT**：每节教材及时落盘，Topic 内容收束和用户学习闭环分开；边界或显式总结再综合，独立复述/实验 waiting 不阻止写作。保留真实个人理解/待验证、机制与证据；结束/切阶段/积累时 checkpoint、阅读入口和下一步。同一固定会话也执行。答疑发现实质文章缺漏同步修订与索引/进度，不凭澄清重写整课。
6. **STAGE CHECK**：核对 exit criteria，尚未交付/尚未评估为正常 in_progress；教材可继续到合理后续内容，未验收阶段仍开放。能力通过才标完成，不能将每个 waiting 变强制测验或补救。阶段综合教材可先合格，能力门禁和文章门禁分别记。
7. **PLAN**：next_action 明确下一源码符号/环节、因果目标、完成条件与必要加载路径，笔记结尾给接续点。交付确认是内部步骤，不是下一课全部目标；能力未验证不标 complete，但不阻止教材继续。如 checkpoint/stage/note 又有增量纳入本次事件与状态，不拖到下次才保存。

这里的 Learning Commit 是文件协议，不是 `git commit`。无需频繁向用户通报。写入失败是例外：明确哪些成果未保存，给一个精简恢复块，保留当前 Topic 并停止依赖成功保存的跨 Topic/Stage 推进；可以继续回答独立问题。

## 断写恢复与单写者

v1 没有跨文件原子事务。发现 state.pending_commit 或 active journal 尾部 pending 时，先核对 journal、实际文件与 deltas。若 state 最后指针落后于 committed 尾部，同样核对并恢复，不能重复生成事件。

用 event ID + 条目 ID 幂等补齐：已有同一 evidence ID 不追加第二份；只完成未写 delta，再校验引用并最终更新 state。发现与后来用户修改冲突，不覆盖；保留 pending 记录，报告具体冲突并保守恢复 current/next_action。中断写导致 JSON 损坏时先保存损坏内容的副本于 reviews/recovery，再用 journal/stage 证据修复；不能删除历史。

共享 `.codelearn/` 状态只由一个主会话写；可选子 agent 仅写独占的指定教材草稿，不写 state/journal/索引/能力或他人稿件。主会话提交前比对 last_event/next_sequence，不一致先重载，不能覆盖其他写者。无锁或并发事务支持，发现持续共享状态并发则要求单写者；不把有界草稿委派误说成共享状态并发安全。

## 源码变化

Resume、Stage 开始/完成、Horizontal Audit、Reconstruction 对照前检查：git branch、HEAD、工作树相关路径差异；commit 不足以发现 dirty/untracked，更不能忽略非 Git 项目。首次用身份清单与相关文件 hash 建立基线；恢复时重新计算当前 Topic/Stage 及即将使用证据的 hash。阶段/最终审计逐分片检查所有 Critical/Important source_refs。

Git 可用时从旧 commit diff 到当前，并包含 working tree 与 untracked；旧 commit 不可用、非 Git 或分支大改时按模块布局与路径 hash 分批比对。不每轮 hash 全仓。基线 hash 未记录就标无法验证并读取相关源码补基线，不能假定没变。

仅受影响的链路、coverage、notes 与 stage review 标 `needs_revalidation`。相关 mastery 保留历史 level 与证据，设置 source_valid=false；语言通用概念不因换 branch 全部失效。对受影响共享边界追相关使用者，不无差别宣告整项目笔记错误。保存变更事件、旧/新出处；重新追踪并问最小预测/复述后恢复有效性。

笔记注明版本、有效性与修订；有效证据不因日期变更而消失。完成状态若关键契约变化则重新打开相关 Stage/项目验收，不把 PROJECT_COMPLETE 当永久事实。
