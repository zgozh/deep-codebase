# 自动技术笔记与质量门禁

## 触发与分工

- Topic Closure：关键机制形成闭环时，更新 journal/knowledge/mastery/coverage；有价值的知识桥梁与个人理解在 knowledge 写清楚，不必每个 trivial topic 写文章。
- Session Checkpoint：用户结束、重要 Topic 结束、切 Stage、当前内容积累或上下文紧张，保存 current/awaiting/next_action 与未解项；无需“帮我保存”。每轮提交使突发结束也能恢复，不能假设宿主一定提前通知上下文压缩。
- Stage Completion：learning exit criteria 通过自动进入 STAGE_SUMMARY，编写详细 Stage Note，质量门禁不通过就修订。无需等待用户说总结。
- Project Completion：全部能力门禁通过后生成 Deep Dive 和 Reconstruction Review，检查通过才标 PROJECT_COMPLETE。

Journal 是结构化认知过程；Notes 是重新编排的正式技术知识。不能复制事件列表、压缩对话或把 AI讲过的术语堆在一起当 Stage Note。

## 写作方法

用 [Stage Note 模板](../assets/templates/stage-note.md)，从当前源码、Stage 合同、相关 journal 事件、知识桥梁、用户问题/误解/实验/测验/真实复述与 mastery 重写。先提纲再逐节搜索证据；重要源码定位和版本保留，代码只摘必要语义段，不嵌全仓全文。

按真实 Stage 覆盖：问题、系统位置、架构/完整链、关键 Class/Method/Interface、输入输出/状态、重要数据结构与 Entity/DTO/VO、配置来源/消费者、异常返回、底层原理、Why/Alternative/trade-off、其他模块关系；再把“我的关键问题、原理解→纠正、gap 补充、Aha、实验预测/观察/解释、Quiz、真实 restatement、自己实现方案、当前能力与待解项”嵌入适当位置。

没有的结构不编造；真实未发生的个人问答/Aha 不硬补，说明无相应事件。有些维度 N/A 有理由。**缺失 required 实验/复述/能力证据是 Stage 未通过，不是用 N/A 模板绕过。** 一般段落写因果与机制，路径列表/图只是支撑；半年后读者要能重建核心运行过程。

初始理解与最终理解分开；引用个人要点标“学习者表述”，AI改写标“整理”且不改变含义。不要把 AI的建议当用户独立设计。源码事实标 code-confirmed、实际观察 runtime-confirmed、文档 documented、设计判断 inferred、未查清 unknown。源码变化时保留旧解释与修订说明，不无声抹除认知历史。

## Note Quality Gate

在 `.codelearn/reviews/<stage-id>-note-quality.md` 记录每项 pass/fail/N/A、章节定位与理由。使用 [review 模板](../assets/templates/review.md)。检查：

1. 业务目的、系统位置、架构及完整调用/数据/返回链可独立读懂。
2. 关键类、方法/接口、数据结构有职责、机制与实际源码定位。
3. 相关配置/加载/消费者、异常与前端状态恢复、必要原理解释充分。
4. 重要 Why、替代方案、trade-off 与跨模块关系有证据；推断已标注。
5. 真实用户问题、误解纠正、知识补充、Aha 在存在时被重建，个人认知过程没有被磨平。
6. 实验含预测/实际观察/解释/范围，Quiz 含真实表现和提示，Restatement 确实来自用户。
7. Mastery 与 evidence 一致，未解问题、未覆盖/未运行范围及 source validity 清楚。
8. 删除全部聊天记录后，只有源码和 `.codelearn/`，半年后仍能恢复该阶段机制、设计判断和个人关键理解。

第 8 项是最终独立阅读测试：遮住对话，仅沿文章引用尝试重建业务链、复述一个关键原理和定位一个改动点。答案依赖“如前所述/聊天里讲过”或失效引用就 fail。修正文档能修的缺失；若缺学习者证据，返回 REMEDIAL/RESTATE 等教学，不能润色造证据。

生成文章本身不提升 mastery。质量门禁 pass 才将 note status=validated；完成 Stage 要同时通过学习门禁和笔记门禁。大量文章可分章节文件，用总入口链接，保持证据索引与独立可读性。

## 最终 Deep Dive

重新综合而非串接 Stage Notes：系统目的/边界、全栈拓扑、关键业务与数据生命周期、工程/运行约束、故障定位与修改影响、跨模块设计 trade-off、个人最重要误解与领悟、已验证实验、知识/coverage 索引、学习者独立重建设计及与原设计比较、Mini Version 产物与实际验证、残余限制。

总笔记允许链接详细 Stage 文章避免重复，但核心架构与链路须能单独读懂。通过同样质量门禁，更新完成 review 与 state；保持所有路径、证据 ID 与来源版本可追溯。
