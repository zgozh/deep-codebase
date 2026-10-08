# Stage Learning Journal

事件区分 source_discovery/备课笔记与 learner-facing teaching；后者记录实际准备交付或已有对话记录的概念、机制、例子/短源码范围。不把文件生成当授课，也不因用户要求重排路线记录失败。模板原有说明按实际事件填写。

填 Stage ID、分片序号、事件范围，删除模板说明。以下事件骨架用于每个有学习价值的交互；填写实际内容，未发生项可省略。

## E000001 — 事件标题

- 时间：实际时间
- status：pending
- Stage / Topic：实际 ID
- 类型：按本轮选择
- source_refs：路径、符号、源版本/hash、证据类型
- 用户问题/初始理解：实际要点或简短原话；无则明确仅为教学事件
- 新知识/纠正：机制、因果与源码依据
- 对话讲授范围：具体问题、实际代码片段/符号、语法/机制、执行与数据/状态变化、返回路径及边界；全景/备课不冒充源码教学
- 交付自检：源码轮关键项是否齐备、仍未知/未教的边界与下一接续点；简记结论，不复制整份检查表
- 能力证据：题目、实际回答要点、independent/hinted/tutor-provided、hint_count、评价
- gap / misconception / aha：实际变化，未解就保留
- mastery / coverage delta：条目 ID、旧→新、证据理由；无独立证据不升档
- experiment：预测、实际运行/未运行、观察、解释及 review 路径
- unresolved：当前未解问题
- writes / deltas：受影响路径与条目、必要恢复内容/旧→新
- checkpoint：是否闭环/待验证
- awaiting：待回答题目与场景，或 null
- next_action：type、target、reason、completion_condition、load

写入过程中保持 pending；projections 校验后改 committed，最后更新 state 指针。
