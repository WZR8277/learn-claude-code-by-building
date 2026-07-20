# Learn Claude Code by Building

## What This Is

这是一个面向个人学习的长期 Python 项目：沿着 `shareAI-lab/learn-claude-code` 新版教程的 `s01_agent_loop` 到 `s20_comprehensive`，在同一个仓库中逐章构建一个可运行的 mini Claude Code。项目同时保存代码演进、自动化测试、运行证据、个人观点和 Git 历史，并把每章成果整理为飞书父文档下的独立子文档。

## Core Value

通过亲手实现、验证和解释每个章节机制，真正掌握 Claude Code 各部分代码逻辑，并最终得到一个可以运行且演进历史清晰的 Python 编码 Agent。

## Requirements

### Validated

- ✓ Python 3.11+ 的 `src` 布局项目可以作为单一演进代码库安装和导入 — existing
- ✓ `mini-claude-code` 与 `python -m mini_claude_code` 共享稳定的 CLI 入口 — existing
- ✓ 基线 smoke tests 覆盖包版本和 CLI 可调用性 — existing
- ✓ 仓库已定义逐章学习、测试、反思、单提交、标签和飞书归档协议 — existing
- ✓ 代码库架构、技术栈、质量约定和主要风险已通过 GSD 映射 — existing
- ✓ s01 Agent Loop 已完成并归档 — commit `b8a21aa`, tag `s01-agent-loop`, home Feishu child `https://jcneiirfaiic.feishu.cn/file/MNAIblpyEolpC6x0oohcmlHjnHb`

### Active

- [ ] 按 `s01`–`s20` 的顺序理解每章目标、核心机制及其相对上一章的增量
- [ ] 在同一个 `src/mini_claude_code/` 包中逐章实现机制，不维护相互割裂的章节代码副本
- [ ] 从 s02 开始，由 Codex 基于上游行为差量实现章节代码，学习者在 PyCharm 中审查 diff 并提出问题
- [ ] 每章补充与新增机制匹配的自动化测试和安全、可复现的运行演示
- [ ] 每章记录学习者的个人观点，并在不改变原意的前提下整理成通顺表达
- [ ] 每章形成一个边界清晰的学习提交和一个匹配的 `sXX-short-name` Git tag
- [ ] 每章完成后，将导读、原理、代码、测试、个人观点和提交证据写入飞书子文档
- [ ] 在飞书父文档维护章节目录、状态和子文档入口
- [ ] 完成 `s20` 后，仓库能够运行一个整合教程核心机制的 Python 编码 Agent
- [ ] 学习者能够用自己的语言解释 Agent Loop、工具调用、上下文、任务管理及综合机制之间的关系

### Out of Scope

- 复制 Claude Code 的闭源正式实现 — 本项目学习公开教程中的 Agent Harness 机制，不声称复刻官方内部架构
- 逐字照抄上游教学代码 — 以理解后的独立实现和个人解释为学习证据
- 为每章维护一套可执行源码快照 — Git commit/tag 已承担历史追溯，运行时代码只保留一套
- 在章节完成前预先批量创建飞书子文档 — 子文档必须反映真实观点、测试和提交证据
- 将其直接作为生产级、自主执行的 Claude Code 替代品 — 当前目标是可运行、可解释的学习实现
- 引入与 Python 教程主线无关的多语言重写 — 跟随作者 Python 代码降低额外认知负担

## Context

- 上游学习主线：`https://github.com/shareAI-lab/learn-claude-code` 根目录新版教程 `s01_agent_loop` 至 `s20_comprehensive`。
- 本地仓库路径因电脑不同而不同；当前电脑路径为 `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-by-building`。不要把某台电脑的绝对路径当作跨电脑事实。
- 飞书父文档按电脑环境选择：在家使用 `https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng`；在公司使用 `https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc`。更新飞书前必须先询问用户当前是在家还是在公司。
- 当前处于 `s02` 准备：s01 Agent Loop 已完成、提交、打标签、推送，并在家飞书父文档下创建子文档。
- 代码库使用一个稳定的 CLI 边界；模块执行、安装后的控制台命令和测试都汇聚到 `mini_claude_code.cli:main`。
- 学习闭环为：本章导读 → 结合上游阅读与讨论 → 增量实现 → 测试/演示 → 个人观点 → 单章提交与标签 → 飞书子文档。
- 助手在每个新章节开始前负责梳理目标、调用链、关键抽象、相对上一章的变化、阅读路径和常见误区；学习者结合代码阅读并输出个人观点。
- 从 s02 开始，助手在讨论完成后负责实现章节差量；学习者在 PyCharm 中查看 diff，有疑问再继续讨论和调整。
- 助手在章节结束时结合前置梳理、润色后的个人观点、测试结果和 Git 证据，生成美观、简洁、可复习的飞书文档。

## Constraints

- **Tech stack**: 使用 Python 3.11+，跟随上游 Python 教程主线 — 避免语言差异干扰对 Agent 机制的理解
- **Code evolution**: 生产代码始终在 `src/mini_claude_code/` 原地演进 — 保持唯一可运行实现
- **Chapter order**: 默认严格按 `s01`–`s20` 顺序推进 — 后续机制建立在前置机制之上
- **Chapter scope**: 每章只引入该章要求的核心增量 — 保持因果关系清晰，避免提前实现模糊学习边界
- **Code quality from s02**: Codex 实现代码时必须保持方法清晰、结构和文件拆分合理，并为关键 Agent 机制保留清楚的中文注释
- **Verification**: 每章必须通过自动化测试并留下可复现运行证据 — “看懂”必须有行为证据支持
- **Git history**: 每章恰好一个聚焦的学习提交和一个匹配标签 — 让提交历史成为可浏览的学习时间线
- **Documentation timing**: 只有在观点、验证和提交齐备后才创建该章飞书子文档 — 防止文档与实际成果脱节
- **Secrets**: `.env`、API key、token 等敏感信息不得进入 Git 或飞书章节文档 — 保证凭据安全
- **Skill policy**: 本项目及所有子代理不得调用或依赖任何名称以 `trn-` 开头的技能 — 遵守全局和项目级 Agent 项目限制
- **Dirty worktree**: 初始化前已存在的 `src/mini_claude_code/cli.py` 未提交修改必须保留并单独确认归属 — 不把用户工作误纳入规划提交

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 使用 Python 实现 | 上游主线本身使用 Python，可把注意力集中在代码逻辑而非语言转换 | — Pending |
| 建立一个持续演进的仓库 | 最终需要得到完整可运行实现，同时可由 Git 追溯每章增量 | — Pending |
| 章节完成对应一次提交和一次标签 | 让每章形成清晰、可回看、可验证的学习单元 | — Pending |
| 每章完成后才创建飞书子文档 | 文档必须包含真实的个人观点、测试结果和提交记录 | — Pending |
| 父文档维护目录，章节作为子文档 | 长期学习材料保持结构清晰且便于导航 | — Pending |
| 使用 GSD 管理长期上下文 | 学习周期较长，需要跨会话保存目标、阶段、决策和进度 | Active |
| Agent 项目禁用全部 `trn-` 技能 | 这是用户明确设定的全局边界，且已写入全局与项目指令 | — Pending |
| 飞书父文档按家/公司环境切换 | 两台电脑对应不同飞书空间，写死单一父文档会导致归档到错误目录 | 在更新飞书前先询问当前位置 |
| s02 起 Codex 实现章节差量，学习者审查 PyCharm diff | 用户只在 s01 手写代码；后续更重视理解、diff 审查和讨论 | Active; see `.planning/CODING_WORKFLOW.md` |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-07-21 after s01 archive and s02 workflow update*
