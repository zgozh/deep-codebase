# 项目扫描、动态路线与查漏

## 最少证据构成完整地图

先读根级指导、README 的目的/运行片段、目录、构建清单、入口、配置样例、部署/CI 清单。用 `rg --files` 或对应工具枚举；注意默认隐藏/忽略规则，定向检查 `.github/`、其他 CI、环境样例等。排除 `.git`、依赖缓存、构建输出、vendored/generated 内容、二进制与 `.codelearn/`，记录排除理由；生成器/锁文件本身及其部署影响仍需列入。

不要执行初始化/安装/启动来代替扫描。没有运行环境也能建立静态地图，运行结果保持 unknown。秘密值不读入笔记，记录变量名、职责及加载路径即可。

自动识别实际存在的前端、后端、数据库、AI、中间件、配置、构建、部署、测试、脚本、CI/CD、Docker、文档，类别可以新增。未出现标为 absent（有检查范围），未查清标 unknown，未枚举分区标 pending。名称并非职责证据；结合调用点、依赖、注解、导入、路由与配置确认。

项目过大时先建模块/目录清单和已枚举文件清单，不大量输出到聊天或一次塞进上下文。Inventory 分模块存储，一行对应源文件，必要时拆关键符号；大型分区继续分片。所有分区包括 pending 的都进 index，后续进入该模块或横向审计时补齐。首课不等所有符号精读；最终审计不能跳过 pending。

## 两张地图

`project-map.md` 用 [模板](../assets/templates/project-map.md) 保存：

1. 架构地图：系统边界、模块/包/子模块、入口、依赖方向、状态/数据所有者、外部服务、运行拓扑。
2. 业务地图：真实用户操作/系统事件、入口、核心功能、关键链路、结果回到用户的路径。

每项关键结论带源码定位及证据类型。README 是线索，不替代实际实现。作者动机只有明确文档能称“作者说”；否则标设计推断，允许判断抽象没有价值。

## Inventory 与分类

使用 [coverage 模板](../assets/templates/coverage.md)。每个条目有稳定 ID、路径/符号、类型、模块、重要度、深度、证据、来源版本、有效性和目标 Stage。移动/改名在原 ID 更新路径，不重置学习历史。

实际识别范围包括但不限于：页面/Component/Store/API/Router，Controller/Service/Domain/Repository/Entity，DTO/VO/BO/PO/Wrapper，Config/Utils/Constants/Exception/Handler，Annotation/Filter/Interceptor/AOP/Security，缓存/MQ Producer/Consumer/Job/Middleware，数据库表/SQL/Migration，AI Provider/Retrieval/Agent/Tool，配置文件/构建/依赖/测试/脚本/Docker/部署/CI/文档。项目没有的类型不创建假条目。

关键数据流/安全/状态一致性/对外契约/启动行为是 Critical；有设计价值或影响多模块是 Important；一般支撑结构是 Normal；无独立机制的机械 helper 是 Trivial。低估了一个 TokenUtils/SecurityUtils 就升级重要度并补路线。避免把文件名后缀当成全局唯一分类依据。

## 路线生成

用 [roadmap](../assets/templates/roadmap.md) 与 [stage](../assets/templates/stage.md) 模板，按以下决策组织，而非固定课程：

- 先一个架构/可观察主流程的 Stage，让学习者知道系统干什么。
- 选有代表性、可追踪、前置依赖较少的关键功能；沿 Vertical Slice 编排后续 Stage。
- 识别先后依赖：数据产生在检索之前、认证在受限操作之前等；只是例子，由当前项目证据决定。
- 前端存在时既覆盖真实 UI 链，也安排启动、路由、响应式/状态、认证、流式接收、取消/异常、API client、环境与构建；不能全部交给后端 Stage 代替。
- 配置/部署/测试等跨链机制可形成专题；先在业务触发点解释职责，之后横向整合。
- 必留 Horizontal Audit、Architecture Review/修改影响验证、Reconstruction 收尾，不要求固定编号。

每个 Stage 在开始前明确：业务问题、系统位置、关键链路/条目、学习者目标、前置知识、可验证 Exit Criteria、实验及评审要求、完成笔记路径。远期 Stage 可为草案，开始前细化，不预写虚假标准答案。首阶段不强制“先补三个月基础”。

Exit Criteria 要指定对象与证据：例如“独立追踪页面发送至流式渲染，包括异常终止”“解释配置优先级并预测覆盖结果”“实验记录含预测、实际观察与解释”。Quiz 必须覆盖关键机制及迁移应用；准确率不能掩盖一个关键错误。非适用项标 N/A 并给理由；不能豁免实际必要能力。

发现新模块/隐藏链路/知识缺口/错序时，以稳定 Stage ID 修改 roadmap revision，记录原因与依赖变化。不得为让进度好看删除未通过的标准；保留原计划与修订证据。当前用户问题优先按教学协议路由，不强制顺序。

## Horizontal Audit

主要 Vertical Stage 后、进入 Reconstruction 前，重新对照实际仓库枚举与 coverage index。按实际存在的所有类型检查未进入主链或深度不足的内容；特别是基础结构、前端、异常链、安全、配置、缓存/MQ/定时任务、SQL/迁移、脚本、Docker/Nginx/CI、测试/依赖管理及文档中的运行约束。

输出 `.codelearn/reviews/horizontal-audit.md`：检查范围、现有类型、未扫描/遗漏项、重要度、当前与目标深度、补学 Stage、源码有效性、合理排除项。任何 Critical/Important 遗漏、pending 分区或关键 stale 证据都不能通过。新增补学 Stage 自动执行；补齐后只复查受影响范围，不每个小修订重新全仓扫描。

基础设施教学要追“为什么需要→谁读取配置→何时建立连接/使用→故障传播→恢复/生产处理→观察信号”，不能停在“这是 Redis”。测试要解释保护的契约、测试分层与盲区，构建/部署要能说明产物如何从源码到可运行系统。
