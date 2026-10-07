# 验证范围与发布检查

[返回 README](../README.md) · [贡献指南](../CONTRIBUTING.md)

## 本地结构检查

Python 3.10+用于维护者检查，不是Skill运行依赖：

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
```

检查name/description/version/许可证、UI调用元数据、JSON与YAML、初始状态/概念模板字段、Markdown本地文件/锚点链接、UTF-8、占位残留与发布路径范围。脚本只读发布文件；输出PASS不代表模型教学行为已验证。

CI使用相同命令。安装发现还可检查：

```bash
npx skills add . --list
```

这只列出Skill，不写目标Agent安装目录。真正安装与跨Agent行为应分别验证，不能从CLI发现成功推断兼容性。

### v1.0.1 发布检查记录

- 仓库校验实际通过：33个发布文件，65个本地链接/锚点，JSON/YAML、版本、初始模板与暂存范围一致。
- 本机官方skill-creator的quick_validate实际返回 `Skill is valid!`。
- `npx skills add . --list` 实际只发现 `deep-codebase-learning`。
- 推送后 `npx skills add git@github.com:zgozh/deep-codebase.git --list` 实际成功克隆远端并只发现该Skill。
- 本环境Git HTTPS克隆遇到连接重置，已验证SSH入口；这属于访问环境问题，不是Skill执行失败。其他环境可按自身Git访问方式安装。

这些是本地与远端发现检查，不代表GitHub Actions结果、市场收录或所有Agent行为通过。

### v1.1.0 笔记规则检查记录

- 本次是 Skill 指令、Markdown 模板与使用文档更新，state schema 仍为 v1；采用 V0 结构/差异检查，未增加运行脚本。
- `python -X utf8 scripts/validate.py` 实际通过：33个发布文件、73个本地链接/锚点，版本与初始记忆契约一致。
- 官方 `quick_validate.py` 实际返回 `Skill is valid!`；`git diff --check` 无错误。
- 对直接受影响规则做桌面推演：同会话重要主题收束自动写笔记；未验收 Stage 的显式总结保留草稿与待答题；自检 pass 不提升能力或制造运行证据；无新内容不重复重写；旧笔记缺核对字段按 unverified 使用。具体边界见示例 E。

桌面推演与结构检查不证明模型已在真实项目执行这些新增行为。本次未重跑早期 A/B/C/D，也未进行新的独立 Agent 教学测试；旧模拟证据不能包装成 v1.1.0 的真实长期效果验证。

## 已有行为证据

最初v1在Codex环境的独立代理上下文中完成A/C/D文件协议模拟，B由另一个全新上下文仅依赖源码和 `.codelearn/` 恢复。模拟项目包含19个源文件，无完整可运行环境。

| 场景 | 实际检查 | 能说明什么 |
|---|---|---|
| A 初始化 | 地图/路线/Inventory/当前合同/事件/awaiting实际写出 | 首轮持久化可演练 |
| B 恢复 | 8份局部记忆、7个hash、原题/等级/阶段保持 | 小型非Git示例可跨上下文恢复 |
| C 误解 | 事件、知识桥梁、返回点、新待答题；L1未升 | AI纠正未被当成独立通过 |
| D缺证据 | 必要条件不足，阶段未完成且无完成文章 | 文件流程门禁可阻止推进 |
| D模拟通过 | 隔离seeded证据、文章/质量记录、下一Stage待答 | 生成及提交流程可演练，非真实能力或运行证明 |

原项目源码指纹保持不变；行为记录在本地审查后整理为公开 [示例](examples.md)。原始聊天、个人路径、临时日志和模拟学习目录没有进入发布包。

v1.0.1补了概念模板/日期格式、学习路径规则、英文触发词及私人数据边界，并以结构/契约校验检查。早期模拟不能被称为对这些新增异常边界的故障注入测试。

## 尚未验证

- 数周/数月真实学习成效，作者级理解不是已证明效果。
- 大型仓库分片、全课程持续运行和最终真实Mini实现。
- 写权限失败、断写/损坏state、持续并发、未知schema及源码大改的全部恢复分支。
- 除Codex之外各Agent的实际行为，自动发现不等于执行可靠。

这些能力的协议存在；不能将其列为全部测试通过。请在真实项目试用，提交可复查、匿名化的最小问题。

## 行为变更如何验收

局部措辞/文档变更做readback、链接和结构检查。教学/持久化行为变更选择直接受影响的场景；如恢复协议改变，就用全新上下文恢复一个真实文件快照。模拟回答要显式标注并隔离；不代答、不上传私人记录、不把静态推演当实际实验。

报告应列实际读取/写入、用户可见回复、证据变化、检查命令及限制。永久加入的脚本检查保护可复用契约，避免仅匹配固定标题/文件数量。

## 发布边界

版本在 `deep-codebase-learning/SKILL.md` 的metadata.version，初始state.skill_version同步。记忆schema_version独立演进；不兼容更新需明确迁移方案，不能覆盖历史。

准备发布时运行本地检查/CLI发现，审查Git暂存文件与差异，确认仅Skill、相关文档及维护校验文件；再提交和推送。创建tag/GitHub Release属于另一个明确发布动作，本次仓库推送本身不声称已创建Release或市场收录。
