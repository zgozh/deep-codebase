# 教学示例与验收边界

[返回 README](../README.md)

以下内容是可阅读的协议示范；示例学习者回答和实验不计入真实 mastery。早期文件流程模拟使用19个源文件的Java+Vue静态fixture，不是大型可运行应用。

## A：第一次在 Java + Vue 项目中学习

用户：“带我深度学习这个项目。”

Agent定位项目根，读指导/依赖/入口，枚举前端、后端、SQL、配置、部署、测试、CI等实际区域，建立双地图和动态路线。未检查部分标pending。创建状态/索引/当前合同与事件；不会一开始输出十页分析。

第一单元可从“点击发送”开始：

```text
Page/Component → API client → HTTP → Controller
→ Service → Storage/Provider → Response/Stream → State → UI
```

讲到关键方法时问一个可预测的问题。例如保存消息在调用供应商之前，那么供应商失败对已保存状态有什么影响？事务和订阅时序不足时明确需要进一步证据。

## B：只凭文件恢复

用户在新会话：“继续学习。”

Agent读取state.awaiting、当前Stage与最近事件，核对相关源码指纹，复现原待答题；不问“上次学到哪里”，不因新会话就认为答过了。若知识隔日遗忘或关键基础薄弱，可先问少量主动回忆题。

早期独立新上下文模拟实际读取8份局部记忆，核对7个源码/身份指纹，只更新state/journal。没有旧聊天，也没有代答题目或提升能力。

## C：错误理解与逐轮记录

用户：“所以 Service 主要就是为了代码复用，对吧？”

Agent指出复用可能是收益，当前Service承担业务规则与副作用顺序；再问增加CLI后哪些职责仍存在，以及HTTP错误映射属于哪个边界。根据真实源码讲解，不断言作者意图。

保存question/misconception/gap/teaching事件、纠正依据、原主线返回点、新待答题。若只有AI解释而没有独立新回答，L1仍为L1，误解保持unresolved。用户独立回答迁移问题后才评估变化。

## D：阶段完成

| 条件 | 缺失时 | 有真实证据时 |
|---|---|---|
| 完整主链和重要原理 | 继续追踪或知识绕行 | 记录独立解释/预测 |
| Quiz/Restatement | waiting或补救 | 记录回答、提示与评价 |
| required experiment | blocked，不伪造Verified | 保存预测、实际观察、解释 |
| source/coverage有效 | needs_revalidation或补学 | 逐条对照目标 |
| 技术文章质量 | 修订；缺个人证据则回教学 | 通过后才Stage complete |

学习门禁通过后，自动重新编写问题、系统位置、完整链、源码机制、数据/配置/异常、原理、Why/Alternative/trade-off及个人认知。文章质量检查要求删除聊天后仍可恢复核心理解。

早期D通过分支用独立模拟目录里的seeded证据测试生成15节文章及8项文档门禁；未运行真实实验。它证明文件流程可以演练，不证明学习者真实通过。真实项目必须重新取得真实证据。

## 从阶段到项目完成

所有Stage讲过仍不足以完成项目。主要业务后要审计配置、对象、异常、安全、前端、测试和运行基础设施。最后学习者先冻结自己的设计，再实现并验证代表核心机制的Mini Version，与原设计比较。

只有架构图或伪代码时标design_reconstructed/implementation_pending；无法运行不宣布PROJECT_COMPLETE。
