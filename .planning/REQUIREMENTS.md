# Requirements: Learn Claude Code by Building

**Defined:** 2026-07-19
**Core Value:** 通过亲手实现、验证和解释每个章节机制，真正掌握 Claude Code 各部分代码逻辑，并最终得到一个可以运行且演进历史清晰的 Python 编码 Agent。

## v1 Requirements

### Core Loop and Tool Dispatch

- [x] **LOOP-01**: 学习者可以运行 s01 Agent Loop，并通过可注入模型客户端观察完整的模型调用、工具请求、工具结果回传和最终响应终止流程
- [x] **TOOL-01**: 学习者可以在 s02 通过简单的 `TOOL_HANDLERS` 映射调用 Bash、读、写、编辑与 Glob 工具，并观察工具结果和未知工具名称如何返回模型；运行行为不超过上游 s02
- [ ] **SAFE-01**: 学习者可以在 s03 区分 deny、ask、allow 三种权限结果，并验证拒绝和未批准调用不会执行实际工具
- [ ] **HOOK-01**: 学习者可以在 s04 通过有序生命周期 Hooks 扩展提示提交、工具调用前后和停止阶段，同时保持原有循环与权限语义

### Single-Agent Effectiveness and Context

- [ ] **TODO-01**: 学习者可以在 s05 使用仅限当前会话的 TodoWrite 状态组织注意力，并解释它与持久任务系统的区别
- [ ] **SUBA-01**: 学习者可以在 s06 创建拥有新上下文、受限工具和有限递归深度的 Subagent，并只把摘要结果返回父 Agent
- [ ] **SKIL-01**: 学习者可以在 s07 发现技能目录、查看精简清单并按需安全加载完整 SKILL.md，而不是把所有技能正文注入上下文
- [ ] **CTXT-01**: 学习者可以在 s08 触发上下文压缩，同时保留工具协议对、继续执行所需状态和可追溯的溢出证据
- [ ] **MEM-01**: 学习者可以在 s09 将经过筛选的事实写入可检查的持久记忆，并在重启后按相关性重新加载，同时排除秘密和不可信指令
- [ ] **PROM-01**: 学习者可以在 s10 根据当前技能、记忆和运行状态确定性组装 System Prompt，并验证状态变化会使缓存失效
- [ ] **RECV-01**: 学习者可以在 s11 针对输出截断、上下文溢出、暂时性错误和不可重试错误采取有界恢复、退避与模型回退策略

### Durable Work and Async Execution

- [ ] **TASK-01**: 学习者可以在 s12 创建、依赖、认领、完成和恢复文件持久化任务，并验证非法依赖、循环与损坏记录不会被静默接受
- [ ] **BGND-01**: 学习者可以在 s13 启动后台任务并立即获得启动结果，随后由单一会话写入者恰好一次地注入完成通知
- [ ] **CRON-01**: 学习者可以在 s14 创建、取消和恢复定时任务，并使用可控时钟验证每个计划时刻只触发一次

### Multi-Agent Coordination and Isolation

- [ ] **TEAM-01**: 学习者可以在 s15 创建具有稳定身份、受限能力、邮箱传输和明确生命周期的 Agent Team
- [ ] **PROT-01**: 学习者可以在 s16 使用带请求 ID 和预期响应类型的结构化协议完成计划评审、请求响应与关闭确认
- [ ] **AUTO-01**: 学习者可以在 s17 运行 WORK、IDLE、SHUTDOWN 自主循环，并通过原子认领确保同一任务不会被多个 Agent 同时取得
- [ ] **WTRE-01**: 学习者可以在 s18 为任务创建、绑定和安全清理 Git Worktree，并明确区分目录隔离与语义冲突解决

### Dynamic Tools and Capstone

- [ ] **MCP-01**: 学习者可以在 s19 使用进程内模拟 MCP 客户端发现并命名空间化动态工具，使其继续经过本地注册、权限和结果规范化边界
- [ ] **COMP-01**: 学习者可以在 s20 组合 s01–s19 的机制，通过离线端到端轨迹和跨机制故障矩阵证明它们仍围绕同一个 Agent Loop 协作
- [ ] **EXPL-01**: 学习者完成 s20 后可以用自己的语言解释 Agent Loop、工具调用、权限、上下文、记忆、任务、并发、团队、Worktree 与 MCP 的关系

### Chapter Learning Evidence

- [ ] **EVID-01**: 每章记录经过核对的上游章节名、学习目标、保持不变的核心约束以及相对上一章的精确增量
- [ ] **EVID-02**: 每章包含新增机制的主要正向路径、关键失败路径和前序能力回归测试，且完整离线测试套件通过
- [ ] **EVID-03**: 每章保存安全、可复现的运行演示，包括命令、相关环境版本、脱敏输入、预期行为、实际结果摘要与退出状态
- [ ] **EVID-04**: 每章由学习者在文档综合前输出个人观点，至少包含一个事前判断、一个意外或失败、一个本地实现选择及一个上游简化点
- [ ] **EVID-05**: 每章只有一个边界清晰且不包含无关改动的学习提交，并创建匹配的 `sXX-short-name` Git tag
- [ ] **DOCS-01**: 每章在代码、测试、演示、观点、提交和标签全部完成后，才在指定飞书父文档下创建对应子文档
- [ ] **DOCS-02**: 每个飞书子文档包含章节导读、机制说明、关键代码路径、测试与演示证据、润色后的个人观点以及不可变的提交和标签信息，并保持美观、清晰、简洁、适合复习
- [ ] **DOCS-03**: 飞书父文档持续维护 s01–s20 目录、学习状态和全部已完成子文档入口
- [ ] **FLOW-01**: 从 s02 开始，Codex 根据上游行为差量实现章节代码，学习者通过 PyCharm diff 审查、提问和确认；方法、结构、中文注释和测试接缝可以改善实现形式，但不得扩大当前章节的运行行为，也不得仅为旧测试向生产代码添加兼容逻辑

## v2 Requirements

### Production Integrations

- **MCP2-01**: 在独立研究和规划后接入真实 MCP SDK、网络传输、OAuth、订阅与生命周期管理
- **PROD-01**: 在教学目标完成后评估生产级沙箱、遥测、会话恢复、信任控制和部署要求
- **FRAME-01**: 在完整掌握底层机制后再评估 Agent 框架、Claude Agent SDK、数据库、消息代理或 asyncio 重构的价值

## Out of Scope

| Feature | Reason |
|---------|--------|
| 复制或声称复刻 Claude Code 闭源正式实现 | 项目目标是学习公开教程中的 Agent Harness 机制 |
| 逐字复制上游教学代码 | 独立重构和个人解释才是掌握证据 |
| 为每章维护独立运行源码副本 | 单一演进代码库配合 Git commit/tag 已能完整追溯 |
| 将权限提示描述为生产沙箱 | 权限策略不等于操作系统级隔离 |
| 在 s19 接入真实 MCP 网络与认证 | 当前章节只验证模拟发现和适配机制，真实集成留待 v2 |
| 在章节完成前批量创建飞书子文档 | 文档必须引用真实观点、测试和提交证据 |
| 与 Python 主线无关的多语言重写 | 避免语言迁移干扰 Agent 机制学习 |

## Definition of Done

- s01–s20 严格按顺序完成，且每章需求均由测试、演示、个人观点、提交、标签和飞书文档共同证明
- 所有章节共享一个持续演进的 `src/mini_claude_code/` 实现和稳定 CLI 入口
- s20 的累计离线回归、端到端轨迹与故障矩阵全部通过
- 学习者能够脱离教程逐部分解释最终 Agent Harness 的控制流、状态边界和安全约束
- 飞书父文档拥有完整目录，并链接全部 20 个已完成章节子文档

## Traceability

每项 v1 需求映射到且只映射到一个阶段。跨章节证据要求由 Phase 20 的完整性审计负责验收，但其约束适用于每个章节的完成门槛。

| Requirement | Phase | Status |
|-------------|-------|--------|
| LOOP-01 | Phase 1 | Complete |
| TOOL-01 | Phase 2 | Complete |
| SAFE-01 | Phase 3 | Pending |
| HOOK-01 | Phase 4 | Pending |
| TODO-01 | Phase 5 | Pending |
| SUBA-01 | Phase 6 | Pending |
| SKIL-01 | Phase 7 | Pending |
| CTXT-01 | Phase 8 | Pending |
| MEM-01 | Phase 9 | Pending |
| PROM-01 | Phase 10 | Pending |
| RECV-01 | Phase 11 | Pending |
| TASK-01 | Phase 12 | Pending |
| BGND-01 | Phase 13 | Pending |
| CRON-01 | Phase 14 | Pending |
| TEAM-01 | Phase 15 | Pending |
| PROT-01 | Phase 16 | Pending |
| AUTO-01 | Phase 17 | Pending |
| WTRE-01 | Phase 18 | Pending |
| MCP-01 | Phase 19 | Pending |
| COMP-01 | Phase 20 | Pending |
| EXPL-01 | Phase 20 | Pending |
| EVID-01 | Phase 20 | Pending |
| EVID-02 | Phase 20 | Pending |
| EVID-03 | Phase 20 | Pending |
| EVID-04 | Phase 20 | Pending |
| EVID-05 | Phase 20 | Pending |
| DOCS-01 | Phase 20 | Pending |
| DOCS-02 | Phase 20 | Pending |
| DOCS-03 | Phase 20 | Pending |
| FLOW-01 | All phases from s02 | Active |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0 ✓
- Duplicate mappings: 0 ✓

---
*Requirements defined: 2026-07-19*
*Last updated: 2026-07-21 after aligning chapter scope with the upstream behavioral ceiling*
