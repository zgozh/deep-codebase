# 完成审读并集中收尾

本入口接收本课已完成充分扩写的稿，不接收仅十章粗稿或仍计划下次展开的prepared稿；若仍有当前未充分章，先回 [expand](expand-lesson.md) 写其正文，不用最终review、交付索引或收尾V0结束本次请求。保留已核未变证据，累计一次实际事实/教学审读覆盖全部适用章内职责及每个真实单元；收尾只补未核范围和跨章输入、概念、时序、结论衔接，不重读整套规范或无新问题的全书。事实从完整输入、真实来源及适用规则推演，再仅凭正文复演；靠审读者经验补出的必要步骤是缺漏。single记self_review；已选delegated时按 [所有权](authoring.md#首次选择与所有权) 由Principal累计独审，作者自查不冒充独审。

充分扩写齐后，先一次汇总已知内容、数量和结构缺口，整批修所属章/单元并复读影响范围，再按[原文装配](writing-io.md#原文part装配与发布)直接从明确顺序的现存有效raw parts装配，每章/单元仅选当前版本，不混入旧draft、preview或candidate造成重复，成对提供source-root与final-note，并显式携本课既有`--min-lines 2000`（复杂课3000），在内存自动渲染真实源码并生成未占用candidate；预览rendered不参加装配，不覆写正式note。必要修正先在所属raw完成本批改动和范围自读，再生成新candidate，不每改一句就重装整书，也不限制真正内容变化后的必要重装。结合已有累计证据一次检查全大纲（整书唯一H1、章H2、5.x H3及七H4，围栏内源码注释不作标题改写）、正文、来源/链接、正常物理行与适用数量；复读影响范围，真正影响跨章/版式再看candidate。累计语义审读完成且candidate数量检查成功后，新note才用assembler单part纯字节发布已审candidate，仍携同一min-lines，不传source-root/final-note；具体命令见写入约定。已有note先保真实完整raw或可靠Git基线，candidate已核且同阈值数量检查成功后按写入约定的宿主纯字节复制例替换；保留candidate，不Move消耗后重建。后续复核读现存candidate/note或沿用未变证据，不再渲染/读源，不用JSON/行数组string cast当正文，不重新推理或重抄整篇。

完整课实际命令如下，示例选普通2000，复杂课两条均用3000；第二条仅在第一条`saved:true`且累计语义审读完成后执行。换成实际workspace、有效part顺序及未占用输出路径，不自制拼接/WriteAllText生成notes替代数量检查：

~~~text
python /path/to/skill/scripts/assemble_note.py --workspace /path/to/project/.codelearn --part 写作/课ID/01.md 写作/课ID/02.md --source-root /path/to/project --final-note notes/阶段/正式课.md --output 写作/课ID/candidate.md --min-lines 2000
python /path/to/skill/scripts/assemble_note.py --workspace /path/to/project/.codelearn --part 写作/课ID/candidate.md --output notes/阶段/正式课.md --min-lines 2000
~~~

事实错、必需源码/解释缺漏、适用总量不足、状态或链接失效必须修；不能为减少轮次交付已知关键错。同一已读scope的全部已见语义缺口汇成一回，给原作者当前必要片段和上下文修所属part，保留正确教学；新发现的真问题仍修，不设一轮放错上限；同类基线缺口反复到晚期才发现属于流程偏差，不能以多轮碎补掩盖。已确认的图标签/链接/锚等窄机械修由当前主会话处理并保其余raw，不要求作者重输出整章。按 [保留规则](authoring.md#返修保留教学内容) 留可恢复基线、正确源码与必要概念/例值/机制及迁移去向，修后只读影响链。审读须对照声称已讲的原始源范围与实际紧邻展示的代码及必要helper，正文讨论过或链接有效不等于已展示。纯保真匹配不证明范围完整、外部行锚或教学通过；图、跨章重述、失败副作用及真实消费者也核实际来源。

与当前理解无关的深挖、措辞美化/同义标题不阻交付；小节预算按教学基线用于规划与诊断，不逐段卡数，整课下限仍适用。第九、十章复述不抵关键位置缺讲，非必要延伸留具体返回点。

沿用 [review](../assets/templates/review.md#教材通读与修订note-quality)：每章/实际单元各一短条，真实已核范围、事实/教学结论、实际源范围、相邻正文及必要解释缺口；其余范围仍实际读，不另建逐组账本、评分器或报告。审读时累计短依据，正式review在note保存成功后写入。必要未核/未补仍draft/prepared，局部通过不升级全课，也不提升学习者能力。

顺序为累计语义审读完成且candidate数量检查成功→正式note保存成功→按 [PERSIST](memory.md#post-turn-learning-commit) 集中review/交付索引/Stage等projections及必要V0→学习事件提交→state最后指针。`below_min_lines`返回所属薄章的现有专用扩写任务，整批缺口写完整part；prepared checkpoint可存，不得先记delivered或交付事件再补正文。核UTF-8、围栏、实际来源/原码、未解析include为零、链接/JSON/指针及本稿正常物理行；实际state新建/相关变化/必要恢复用check_state核v1结构与对象型source_refs，不将结构通过说成教学或掌握通过。数量口径与原预算一致，不能用排除空行计数或旧示例替代；未变证据不重跑，仅最后指针变化就查相关JSON/指针。完整教材满足内容与保存条件才ready/delivered，聊天简短给主题、范围和入口；交付不证明用户已读或掌握。

按实际覆盖确定唯一下一教学符号/问题，同步note结尾、roadmap、Stage、journal与state；旧计划中已教内容不再排作下一课。state最终指针只在正式note成功后写；若事件或状态曾提前提交，如实记录偏差与当前修复，不改写当时历史。

工具异常沿 [既有恢复](writing-io.md)：一次定位错误类别并修请求/换可靠载体，不重复不变的坏请求，不用probe污染教材，不缩稿掩盖未保存。真实中断/反馈及时最小checkpoint，不等整课成功；无应用改动不跑应用测试、构建或浏览器。
