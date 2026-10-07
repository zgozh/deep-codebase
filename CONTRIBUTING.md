# 贡献指南

[返回 README](README.md)

欢迎反馈真实学习中遇到的卡点、恢复问题、遗漏区域、误判掌握度、文章质量问题及不同Agent的兼容性。

## 提交问题

在 [Issues](https://github.com/zgozh/deep-codebase/issues) 描述：Skill版本、Agent/平台、期望行为、实际行为、匿名化的最小复现、相关文件结构和已运行检查。明确哪些是源码事实、用户回答、实际运行或模拟数据。

不要公开私人源码、完整聊天、凭证或个人 `.codelearn/`。可用虚构的小型fixture重现，但必须标注模拟边界。

## 修改与检查

1. Fork并创建工作分支。
2. 让改动针对一个具体行为；保持SKILL入口短，详细协议放references，产物骨架放assets/templates。
3. 运行 `python -m pip install -r requirements-dev.txt` 和 `python scripts/validate.py`。
4. 涉及安装目录或发现方式时运行 `npx skills add . --list`；涉及行为时执行直接相关的隔离场景。
5. PR说明触发问题、结果行为、实际证据及限制。不要将未执行的检查写成通过。

不需要每个文档修订重跑全部模拟。修复发现的真实问题；不要堆叠所有Topic强制问卷、无条件全仓读取、默认应用全套测试或后台服务。

## 核心不变量

- 用户只需自然语言开始与继续，不维护进度命令。
- 理解依据真实独立表现，不依据“懂了”或AI讲过。
- Journal保留认知过程，Notes重新编写知识。
- 有前端就覆盖UI完整链，横向审计不能漏重要支撑结构。
- 保存及恢复只在明确项目内；模拟证据不能污染真实能力。
- 无真实必要实验或独立Mini实现，不能宣布相关最终门禁通过。

## 版本与兼容性

更新行为时同步 [CHANGELOG](CHANGELOG.md)、SKILL metadata.version和初始state.skill_version。schema_version只在学习记忆格式兼容性需要时改变；给出旧记录处理方式，未知版本不得默认重置。

贡献以本项目 [MIT License](LICENSE) 发布。引用上游设计时补出处；直接复用上游内容需保留相应许可声明，不只放一个致谢链接。
