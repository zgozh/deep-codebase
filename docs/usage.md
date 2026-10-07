# 使用指南

[返回 README](../README.md)

## 安装与发现

推荐 Skills CLI，根据所用 Agent 选择安装目标：

```bash
npx skills add zgozh/deep-codebase --skill deep-codebase-learning -g
```

`--skill` 指定本仓库中的 Skill，`-g` 表示用户级安装；`-a codex` 可限定 Codex，`-y` 可跳过安装器确认。省略 `-g` 则安装到当前项目。安装器支持的 Agent 和目录以 [其官方文档](https://github.com/vercel-labs/skills) 为准；本项目不声称所有 Agent 已经过行为测试。

本机HTTPS访问不可用、但已经配置GitHub SSH访问时，可使用完整SSH地址：

```bash
npx skills add git@github.com:zgozh/deep-codebase.git --skill deep-codebase-learning -g
```

SSH访问需要你的GitHub密钥权限；不要求把密钥或token写入Skill。无法使用SSH时也可下载仓库并从本地目录安装：`npx skills add ./deep-codebase --skill deep-codebase-learning -g`。

没有 Node/npm 也可以直接复制整个 Skill 文件夹。下面是本项目已采用的 Codex 用户目录；若设置了 `CODEX_HOME`，按自己的配置使用其 `skills/`。

### macOS / Linux 手动安装

确认目标不存在再运行；已有版本先查看下方更新说明。

```bash
git clone https://github.com/zgozh/deep-codebase.git
mkdir -p ~/.codex/skills
cp -R deep-codebase/deep-codebase-learning ~/.codex/skills/
```

### Windows PowerShell 手动安装

```powershell
git clone https://github.com/zgozh/deep-codebase.git
$skillRoot = Join-Path $env:USERPROFILE '.codex/skills'
$skillTarget = Join-Path $skillRoot 'deep-codebase-learning'
if (Test-Path -LiteralPath $skillTarget) { throw 'Existing skill: use the update instructions.' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Copy-Item -LiteralPath './deep-codebase/deep-codebase-learning' -Destination $skillTarget -Recurse
```

其他 Agent 使用其支持的 Skills 目录。复制文件夹时不要改名；`deep-codebase-learning` 必须与 frontmatter 的 name 相同，`references/` 和 `assets/` 需要一起复制。不要只复制 SKILL.md。

安装后在目标项目打开新会话。若 Agent 提供技能列表，确认包含 `deep-codebase-learning`；Codex 可显式调用 `$deep-codebase-learning`。本 Skill 自动发现默认开启，其他 Skill 同时匹配时显式调用有助于消除歧义。

## 第一次学习

打开真实源码项目而非 Skill 安装目录，说“带我深度学习这个项目”。可以顺带说背景，例如“我会基础 Java，但不熟悉 Spring”。不需要先填写长问卷。

Agent 会识别项目根、扫描实际模块、建立 `.codelearn/`，简洁介绍项目和路线，开始一个小教学单元。大项目先完整枚举范围，再分区细化；未检查的内容保留 pending/unknown，不冒充完整理解。

多仓库工作区可明确“学习 `backend/` 和 `frontend/` 组成的系统”。若项目根无法判断，Agent 会只澄清这个必要信息。路径不可访问或写权限不足时会报告真实限制。

## 继续、提问与结束

“继续学习”读取当前位置、待答题、返回点、近期认知变化和相关源码，判断是否先复习。通常先接原待答题，而非要求你回忆上次停在哪。

随时可以问：“这一行是什么意思？”“为什么用 DTO？”“先直接解释，不要考我。”路线不会阻止即时问题。直接解释不构成独立掌握证据。

“今天到这里”触发检查点，保留下一动作。即使会话突然结束，已执行的有意义交互应已保存；不能保证 Agent 在外部强制中断前尚未完成的文件写入。发生断写时下次先检查 pending 事件。

## 实验与开发模式

实验通常由你先预测，再尝试修改/运行，最后解释观察。Agent 可在已有授权范围内协助，但不会把学习调用视为运行生产操作或付费 API 的许可。

环境缺失时可继续静态追踪或设计离线实验；未运行不会标 Verified。必要实验 blocked 时，相关阶段保留未完成。

如果明确说“现在不是学习，请直接完成这个开发任务”，Agent 保存学习检查点并尊重开发目标。以后回到学习，会结合实际改动重新检查源码证据。

## 学习记忆由你管理

`.codelearn/` 在目标项目内，不在 Skill 安装目录。它保存结构化知识与个人理解，不保存完整聊天。

是否加入 Git、忽略、加密备份或仅本地保留由你决定。里面可能包含内部路径、你的回答和错误理解，不要随意公开。这个发布仓库的 `.gitignore` 只管理本仓库的本地开发材料，不会修改被学习项目的忽略规则。

同一个学习目录同时使用一个写入会话。不同项目可各自学习；多人共享项目不应混用同一份个人 mastery/state。v1不实现多人账户或并发合并。

## 更新 Skill

用 CLI 安装时可使用 `npx skills update`；作用范围与当前安装以安装器提示为准。手动安装时先更新克隆的仓库，核对版本与 [CHANGELOG](../CHANGELOG.md)，再替换**安装目录中的 Skill 文件**，不要删目标项目的 `.codelearn/`。

更新前可备份安装目录；不要在包含用户定制内容的文件夹上盲目覆盖。学习记忆的 schema_version 和 Skill version 分开：新 Skill 遇到未知 schema 只读报告，不自动重置或迁移历史。

## 常见问题

**没有自动启动？** 新会话中显式调用 Skill，检查安装了正确的整个文件夹，并确认打开的是目标项目。

**读了很多却总在被问问题？** 可以说希望先解释或降低题目难度；但独立能力证据仍需通过真实回答/尝试取得。

**阶段为什么未完成？** 让 Agent 说明当前 exit criteria 的缺项。必要实验、关键误解、个人复述或文章质量门禁未通过都会保留未完成。

**换分支后旧笔记还能用吗？** 先检查相关源码；仅受影响的记录标 needs_revalidation，通用语言知识不会因切分支全部清零。

**文件写入失败？** 不要把未保存进度当成功。Agent 应给出简短恢复记录；恢复写权限后先补齐再跨 Topic。
