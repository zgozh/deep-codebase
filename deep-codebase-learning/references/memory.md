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
  knowledge/index.md         gap/误解/问题/术语的可搜索索引
  knowledge/<topic-id>.md    知识桥梁与个人理解
  notes/index.md             已生成文章、事件边界、核对状态与阅读入口
  notes/topics/<stage-topic>.md  重要主题的详细文章，可先于能力验证生成
  notes/sessions/<session-id>.md 显式会话整理（按实际事件范围）
  notes/<stage-id>.md        阶段综合文章，未完成时可有草稿
  notes/deep-dive.md         完成后的总知识地图与跨模块综合
  reviews/<review-id>.md     Quiz/实验/阶段评审/审计/重建证据
```

只创建已用到的文件；首轮至少 state、roadmap、project-map、当前 stage、三个 index 及当前分片。空列表表示尚无证据，不生成不存在的模块。使用 [state](../assets/templates/state.json)、[mastery](../assets/templates/mastery.json)、[coverage](../assets/templates/coverage.md)、[journal](../assets/templates/journal.md) 模板。

所有文本使用 UTF-8。Windows PowerShell 读取中文必须显式 `Get-Content -Encoding UTF8`，写入用明确 UTF-8 的文件工具；不要依赖系统默认编码。给 Windows PowerShell 5.1 执行的含非 ASCII 脚本用 UTF-8 BOM 或不含非 ASCII 的脚本内容，避免模板/日志乱码被误当成学习状态损坏。

state 的必需字段：`schema_version`、`skill_version`、`project`（name、root_hint、revision、identity_sources）、`learner`（背景已知/未知、目标、语言）、`mode`、`phase`、`current`（stage/topic/source_refs）、`return_points`、`awaiting`、`next_action`、`focus_files`、`journal`（active_file/last_event/next_sequence）、`open_loops`、`pending_commit`、`updated_at`。

初始化时按实际用户语言和目标填写 learner，未知背景保持 unknown；模板文本不构成用户能力证据，也不锁定教学语言。日期使用 ISO 8601，未发生的时间用 null，不虚构历史。

- 路径相对项目根；root_hint 只帮助发现迁移，不能作为唯一身份或失效依据。模块/Stage/Concept/Event ID 稳定且全项目唯一。迁移目录时优先根据源码身份与布局判断，不盲写旧绝对路径。
- state/focus_files/journal/rubric/next_action 中的学习记忆路径统一相对项目根，如 `.codelearn/stages/S01.md`；Markdown点击链接则相对所在文档。读取或恢复写入前解析路径，记忆写入必须位于当前项目 `.codelearn/`，不得跟随逃出该目录的软链接；source_refs 位于当前项目内。超范围路径作为未知/冲突处理，不自动访问。
- `revision` 存 git branch/commit（无 Git 可 null）及相关源码内容指纹。SHA256 用宿主工具计算，不自行生成假的 hash。每个 source_ref 至少 path、symbol（可空）、revision/hash、evidence_kind。相同版本共享 revision，已 dirty 或非 Git 源文件保存内容 hash。
- `awaiting` 为 null 或 `{kind, prompt, topic, source_refs, issued_event, rubric_ref}`；保存学习者看到的问题和场景，评分标准放 reviews 文件按需读。尚未回答不能当失败或通过。
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

Session checkpoint 保留上述位置，不增加用户操作。阶段结束自动选择下一动作，但到需要用户新证据时等待，不能扮演学习者。

## Journal 与事件

每个 meaningful interaction 提取一个或少量事件，用稳定 `E000001` 连号。事件按模板保存：类型（question/answer/reasoning/misconception/gap/insight/aha/source_discovery/prediction/experiment/quiz/restatement/mastery_change/coverage_change/design_decision/unresolved/teaching/checkpoint 等可组合）、Stage/Topic、source_refs、用户原理解或简短原话、纠正与依据、独立证据/提示、认知变化、未解项、下一动作。

完整 transcript 禁止。保留关键问题、关键个人表述和实验结果；AI长讲解提炼成可重建的机制/链路/出处，不能只写“讲了 SSE”。涉及敏感值用占位符。Aha 是用户实际表达的领悟，不能替用户杜撰。

事件额外有 `status: pending|committed`、`writes` 与必要 `deltas`：记录受影响文件/条目、旧值→新值及足够恢复的内容。writes 是路径清单，不复制整份 Notes。L0→L1 可以是讲过；L3 及以上须包含用户独立表现。一个 answer 不意味着其他概念都提升。

每片约 100 个事件或 32 KiB 时开新片；这是导航阈值，不删除旧事件。阶段评审记录其使用的事件范围/文件以便 Notes 重建。只读近期尾部与相关 ID；历史可 `rg` 搜索。重要 Topic 讲解收束按 [笔记协议](notes.md) 写详细主题文章，不能仅留一行日志；notes/index.md 记录稳定 ID、文章路径、覆盖事件/最后整理事件、quality/verification、未解项。显式会话总结需要事件边界：首次进入该会话的 journal checkpoint 记录 session ID/首事件；已有会话边界缺失时只写可恢复的范围，不猜完整历史。会话元信息存在 journal/notes index，不扩充或迁移 state schema。

## PRE-TURN LOAD

每次新会话/“继续学习”执行完整协议；同会话继续时复用已加载协议和未变状态，只读必要变更。

1. 查 `.codelearn/state.json`。不存在时检查残留目录和其他学习记忆，避免覆盖；真正全新才初始化。目录存在却 state 丢失则从 roadmap、阶段合同与最近 committed 事件重建保守检查点，不能当新学习者抹掉成果。
2. 核对 schema/项目身份，恢复 pending（下节）。读 roadmap 当前行及依赖、当前 stage、state 指向的当前 mastery/coverage/knowledge/review；近期 journal 默认最后 3–5 个有价值事件。不要打开全部历史。
3. 检查源码变化（后文）。相关失效先重新定位，不能沿过期方法继续教学。
4. 找 awaiting、知识绕行 return_point、阻塞误解、未解问题、上次 next_action；结合 mastery 和 source validity 决策。隔日/隔周、遗忘迹象或 prerequisite 薄弱才安排 recall，不能每次机械重考。
5. 简短自然定向并开始一个动作。若等待用户回答，复现已保存题目/最小上下文；只有记录确实缺失才请用户补充。

上下文初始预算通常 5–8 个短文件/局部段落，state 尽量 <8 KiB。遇大文件搜索 ID/标题再读相关段落；源码只读当前符号及一跳必要依赖，证据不足再扩大。Notes 生成是阶段边界任务，可以按提纲逐节读取证据并写作，不一次加载整段历史。不能为了省 context 猜测。

## POST-TURN LEARNING COMMIT

每轮处理完用户消息、准备回复后，结束响应及转新 Topic 前执行。用户没有回答时也保存本轮讲解/发现与将发出的问题；问候等无学习变化只保留必要状态，不造事件。

1. **CLASSIFY**：判定有哪些学习事件，回答是否 independent/hinted/tutor-provided。
2. **EXTRACT**：提取新事实、出处、用户理解、错误/纠正、问题、预测、实际结果；不要捏造未运行观察。
3. **EVALUATE**：按证据判断 mastery/coverage 变化、gap/misconception、源码有效性。无独立回答时不提升 L2+。
4. **PERSIST**：先追加 pending 事件（writes/deltas），再写 state.pending_commit 指向它；按条目更新 projections：coverage、mastery、knowledge、相关 review/stage/roadmap/note；检查 JSON 可解析、引用可定位、差异正确，尤其核对 coverage/Concept ID 对应的实际路径与符号（文件存在不能证明 ID 指向正确）；把事件改 committed；**最后**更新 state（last_event/next_sequence/current/awaiting/next_action，清 pending）。尚未收到的问题写 awaiting，不能写成已经答对。回复已准备不证明学习者看过或理解，最多记录 teaching 与待答状态。
5. **CHECKPOINT**：每轮判断重要 Topic 的讲解收束与学习闭环，二者分开；讲解收束或显式总结时按 [笔记协议](notes.md) 写详细文章，即使独立复述/实验仍 waiting。保留个人 restatement 或“尚待验证”、机制、关键证据及当前有效性；明显结束/切阶段/内容积累时保存 session checkpoint、笔记阅读入口和 next_action。同一会话正常持续也执行，不能等新会话或所有 Stage 门禁通过才写主题笔记。
6. **STAGE CHECK**：核对该 Stage exit criteria，有缺口则 next_action=remedial；通过才进入笔记生成/门禁。
7. **PLAN**：生成下一最合理动作并持久化；如 checkpoint/stage/note 又产生增量，在本次提交结束前纳入对应事件和状态，不能把它们留到下次才保存。

这里的 Learning Commit 是文件协议，不是 `git commit`。无需频繁向用户通报。写入失败是例外：明确哪些成果未保存，给一个精简恢复块，保留当前 Topic 并停止依赖成功保存的跨 Topic/Stage 推进；可以继续回答独立问题。

## 断写恢复与单写者

v1 没有跨文件原子事务。发现 state.pending_commit 或 active journal 尾部 pending 时，先核对 journal、实际文件与 deltas。若 state 最后指针落后于 committed 尾部，同样核对并恢复，不能重复生成事件。

用 event ID + 条目 ID 幂等补齐：已有同一 evidence ID 不追加第二份；只完成未写 delta，再校验引用并最终更新 state。发现与后来用户修改冲突，不覆盖；保留 pending 记录，报告具体冲突并保守恢复 current/next_action。中断写导致 JSON 损坏时先保存损坏内容的副本于 reviews/recovery，再用 journal/stage 证据修复；不能删除历史。

只允许一个 Agent 会话写当前 `.codelearn/`；提交前比对 state.last_event/next_sequence 与本轮加载值，不一致则重新载入，不覆盖另一会话。无锁机制，不声称支持并发事务；发现持续并发请用户只保留一个学习写入会话。

## 源码变化

Resume、Stage 开始/完成、Horizontal Audit、Reconstruction 对照前检查：git branch、HEAD、工作树相关路径差异；commit 不足以发现 dirty/untracked，更不能忽略非 Git 项目。首次用身份清单与相关文件 hash 建立基线；恢复时重新计算当前 Topic/Stage 及即将使用证据的 hash。阶段/最终审计逐分片检查所有 Critical/Important source_refs。

Git 可用时从旧 commit diff 到当前，并包含 working tree 与 untracked；旧 commit 不可用、非 Git 或分支大改时按模块布局与路径 hash 分批比对。不每轮 hash 全仓。基线 hash 未记录就标无法验证并读取相关源码补基线，不能假定没变。

仅受影响的链路、coverage、notes 与 stage review 标 `needs_revalidation`。相关 mastery 保留历史 level 与证据，设置 source_valid=false；语言通用概念不因换 branch 全部失效。对受影响共享边界追相关使用者，不无差别宣告整项目笔记错误。保存变更事件、旧/新出处；重新追踪并问最小预测/复述后恢复有效性。

笔记注明版本、有效性与修订；有效证据不因日期变更而消失。完成状态若关键契约变化则重新打开相关 Stage/项目验收，不把 PROJECT_COMPLETE 当永久事实。
