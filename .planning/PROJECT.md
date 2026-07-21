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
- ✓ s01 Agent Loop 已完成并归档 — commit `b8a21aa`, tag `s01-agent-loop`, home Feishu docx child `https://jcneiirfaiic.feishu.cn/wiki/WkW6wgMnbifIiTkFuUGcEhYhnWf`
- ✓ s02 Tool Use 已完成并归档 — tag `s02-tool-use`, company Feishu docx child `https://trip.larkenterprise.com/wiki/MwfHwn0Lwi4b9XkWNNUcFUmgnth`
- ✓ s03 Permission 已完成并归档 — tag `s03-permission`, company Feishu docx child `https://trip.larkenterprise.com/wiki/DqXEw21KWiuzWDkCA6CcYzLAn4g`
- ✓ s04 Hooks 已完成并归档 — commit `8ce0806`, tag `s04-hooks`, home Feishu docx child `https://jcneiirfaiic.feishu.cn/wiki/PNNRwDIetiz7OjkAdmocdDHenfe`
- ✓ s05 TodoWrite 已完成并归档 — commit `8efa890`, tag `s05-todo-write`, home Feishu docx child `https://jcneiirfaiic.feishu.cn/wiki/Dmf6wxoNXimqWbkRT1mcFVEXnid`
- ✓ s06 Subagent 已完成代码、测试、diff 审查与个人反思 — final commit/tag/Feishu archive in progress

### Active

- [ ] 按 `s01`–`s20` 的顺序理解每章目标、核心机制及其相对上一章的增量
- [ ] 在同一个 `src/mini_claude_code/` 包中逐章实现机制，不维护相互割裂的章节代码副本
- [ ] 以上游当前章节的可运行行为作为功能上限；代码风格、中文注释、模块拆分和测试接缝只改善表达与可测试性，不增加教程之外的功能
- [ ] 从 s02 开始，由 Codex 先给出简短导读和 diff 阅读提示，再基于上游行为差量实现未提交的章节代码；学习者看过 PyCharm diff 后再提出问题和确认，不要求实现前预选讨论主题
- [ ] 每章补充与新增机制匹配的自动化测试和安全、可复现的运行演示
- [ ] 每章记录学习者的个人观点，并在不改变原意的前提下整理成通顺表达
- [ ] 每章形成一个边界清晰的学习提交和一个匹配的 `sXX-short-name` Git tag
- [ ] 每章完成后，将导读、原理、代码、测试、个人观点和提交证据写入飞书子文档
- [ ] 在飞书父文档维护章节目录、状态和子文档入口
- [ ] 每个飞书子文档必须美观、清晰、简洁、适合复习，不得直接上传本地 Markdown 拼接稿作为最终版本
- [ ] 完成 `s20` 后，仓库能够运行一个整合教程核心机制的 Python 编码 Agent
- [ ] 学习者能够用自己的语言解释 Agent Loop、工具调用、上下文、任务管理及综合机制之间的关系

### Out of Scope

- 复制 Claude Code 的闭源正式实现 — 本项目学习公开教程中的 Agent Harness 机制，不声称复刻官方内部架构
- 逐字照抄上游教学代码 — 以理解后的独立实现和个人解释为学习证据
- 以“代码质量”或“安全性”为理由提前增加当前章节未教授的能力、校验、防护、错误语义或未来机制 — 如确有需要，必须先获得学习者明确同意
- 为每章维护一套可执行源码快照 — Git commit/tag 已承担历史追溯，运行时代码只保留一套
- 在章节完成前预先批量创建飞书子文档 — 子文档必须反映真实观点、测试和提交证据
- 将其直接作为生产级、自主执行的 Claude Code 替代品 — 当前目标是可运行、可解释的学习实现
- 引入与 Python 教程主线无关的多语言重写 — 跟随作者 Python 代码降低额外认知负担

## Context

- 上游学习主线：`shareAI-lab/learn-claude-code` 根目录新版教程 `s01_agent_loop` 至 `s20_comprehensive`。当前电脑已下载本地教程副本：`/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main`；以后比较章节差量时优先读这个本地目录，只有本地缺失、明显过期或用户要求验证远端时才联网。
- 本地仓库路径因电脑不同而不同；已知检出路径包括 `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-by-building` 和 `/Users/zhaorongwang/agentprojects/learn-claude-code-by-building`。每次以当前仓库根目录为准，不把任一路径当作跨电脑事实，也不根据路径猜测家里/公司环境；涉及环境相关操作时先询问用户当前是在家还是在公司。
- 飞书父文档按电脑环境选择：在家使用 `https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng`；在公司使用 `https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc`。更新飞书前必须先询问用户当前是在家还是在公司。
- 当前处于 `s06` 收尾：s01 Agent Loop、s02 Tool Use、s03 Permission、s04 Hooks 与 s05 TodoWrite 已完成并归档；s06 Subagent 已完成代码、测试、diff 审查与个人反思，正在进行最终 commit、tag 与飞书归档。
- 代码库使用一个稳定的 CLI 边界；模块执行、安装后的控制台命令和测试都汇聚到 `mini_claude_code.cli:main`。
- 学习闭环为：简短导读与 diff 关注点 → 增量实现及测试/演示（保持未提交）→ 学习者审查 PyCharm diff、讨论并输出个人观点 → 调整确认 → 单章提交与标签 → 飞书子文档。
- 助手在每个新章节开始前负责梳理目标、调用链、关键抽象、相对上一章的变化、阅读路径和常见误区；学习者结合代码阅读并输出个人观点。
- 从 s02 开始，助手在简短导读后直接实现章节差量，不把实现前讨论或预选讨论主题作为门槛；学习者在 PyCharm 中查看实际 diff 后，再围绕代码提问、讨论和要求调整。
- 助手在章节结束时结合前置梳理、润色后的个人观点、测试结果和 Git 证据，生成美观、简洁、可复习的飞书文档。

## Constraints

- **Tech stack**: 使用 Python 3.11+，跟随上游 Python 教程主线 — 避免语言差异干扰对 Agent 机制的理解
- **Code evolution**: 生产代码始终在 `src/mini_claude_code/` 原地演进 — 保持唯一可运行实现
- **Chapter order**: 默认严格按 `s01`–`s20` 顺序推进 — 后续机制建立在前置机制之上
- **Chapter scope**: 上游当前章节的可运行代码和讲解是本章行为上限；先与上一章比较并只实现精确增量 — 保持因果关系清晰，避免提前实现模糊学习边界
- **Code quality from s02**: Codex 实现代码时必须保持方法清晰、结构和文件拆分合理，并为关键 Agent 机制保留清楚的中文注释；这些要求只约束实现形式，不授权增加功能
- **Test integrity**: 测试应适配当前生产接口；除非向后兼容本身是当前章节要求，不得仅为保留旧测试而在生产代码中增加旧参数、兼容分支、回退行为或重复执行路径
- **Planning precedence**: 学习者明确决定、`AGENTS.md` 和上游当前章节优先于早期研究建议或旧规划措辞 — 避免历史文档重新扩大章节范围
- **Verification**: 每章必须通过自动化测试并留下可复现运行证据 — “看懂”必须有行为证据支持
- **Git history**: 每章恰好一个聚焦的学习提交和一个匹配标签 — 让提交历史成为可浏览的学习时间线
- **Documentation timing**: 只有在观点、验证和提交齐备后才创建该章飞书子文档 — 防止文档与实际成果脱节
- **Feishu quality**: 飞书子文档必须是面向复习的精炼成稿，不能只是 `guide.md`、`reflection.md`、`evidence.md` 的原样拼接
- **Secrets**: `.env`、API key、token 等敏感信息不得进入 Git 或飞书章节文档 — 保证凭据安全
- **Skill policy**: 本项目及所有子代理不得调用或依赖任何名称以 `trn-` 开头的技能 — 遵守全局和项目级 Agent 项目限制
- **Clean handoff**: 每章开始和结束都检查 `git status --short --branch`，确认没有未解释的用户改动或跨电脑同步遗漏

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
| s02 起先导读、再实现未提交差量、后看 diff 讨论 | 用户只在 s01 手写代码；后续以实际 diff 作为学习讨论材料，不要求学习者在代码出现前预选问题或确认就绪 | Active; see `.planning/CODING_WORKFLOW.md` |
| 上游当前章节行为是功能上限 | 用户要求改善代码风格、中文注释和架构，但没有授权新增教程之外的功能；独立实现也不等于扩大设计 | Active; engineering quality may change form, never chapter scope without explicit approval |
| 上游教程优先使用本地副本 | 用户已把远程教程下载到本机，项目名为 `learn-claude-code-main`，可避免每次联网和远端不稳定 | Active; home path `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main` |
| 旧测试不得腐化生产代码 | 章节演进后应修改旧测试以使用当前接口，不应为测试保留过时参数或兼容分支；只有章节明确教授向后兼容时例外 | Active; tests follow the production design |
| 飞书子文档必须美观清晰简洁，且使用真正的飞书在线文档 | 用户明确指出 s01 原始 Markdown 上传不符合复习质量要求 | Active; s01 home docx has been corrected; see `.planning/FEISHU_SYNC.md` |

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
*Last updated: 2026-07-21 while finalizing s06 Subagent*
