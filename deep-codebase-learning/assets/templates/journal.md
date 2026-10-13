# Stage Learning Journal

按记忆协议分开 investigated、prepared、delivered、explained 与 learner-evidence。正式笔记保存/回读/内容门禁/V0/索引成功才 delivered；草稿和拟发聊天 prepared，实际聊天解释才用可见依据确认。pending/committed 是文件写入状态，交付不等于阅读/能力。按真实事件填，未发生项省略。

填 Stage ID、分片序号、事件范围，删除模板说明。以下事件骨架用于每个有学习价值的交互；填写实际内容，未发生项可省略。

## E000001 — 事件标题

- 时间：实际时间
- status：pending
- Stage / Topic：实际 ID
- 类型：按本轮选择
- source_refs：路径、符号、源版本/hash、证据类型
- 用户问题/初始理解：实际要点或简短原话；无则明确仅为教学事件
- 新知识/纠正：机制、因果与源码依据
- investigated：查过的源码/版本/官方章节，不能算授课
- prepared：拟交付因果目标、必须前置、概念解释深度、真实注释片段源锚点、调用/状态/返回因果、具体例子/限制和仍未展开边界
- delivered：正式教材路径/课ID/当前起止、版本、quality/verification、review 与 V0，索引及链接已确认；无则省略
- explained：合格教材段落或实际可见聊天/原事件 ID 与解释深度，未展开内部明确；不证明用户阅读/掌握
- 教学偏好/修复项：最新交付渠道、详细度/名词全称/注释/官方内容要求，single/delegated 选择/已询问记录；持续应用，漏讲不记用户失败
- 交付自检：源码轮关键项是否齐备、仍未知/未教的边界与下一接续点；简记结论，不复制整份检查表
- learner-evidence：题目、真实回答/预测/实现、independent/hinted/tutor-provided、hint_count、评价；与讲授范围分开
- gap / misconception / aha：实际变化，未解就保留
- mastery / coverage delta：条目 ID、旧→新、证据理由；无独立证据不升档
- experiment：预测、实际运行/未运行、观察、解释及 review 路径
- unresolved：当前未解问题
- writes / deltas：受影响路径与条目、必要恢复内容/旧→新；改名含中文阶段目录映射及所有相关引用
- checkpoint：是否闭环/待验证
- awaiting：待回答题目与场景，或 null
- next_action：type、target、reason、completion_condition、load

写入过程中保持 pending；projections 校验后改 committed，最后更新 state 指针。
