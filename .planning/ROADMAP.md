# Roadmap: Learn Claude Code by Building

## Overview

本路线图严格沿用上游 `s01_agent_loop` 到 `s20_comprehensive` 的顺序，在同一个 Python 包中逐章扩展一条可运行的 Agent Loop。每个阶段只引入该章机制，并以自动化测试、安全演示、学习者反思、一个聚焦提交、一个匹配标签和一个飞书子文档形成完整学习闭环；后续阶段必须保留前序阶段的行为契约。

## Phases

**Phase Numbering:**
- Integer phases (1-20): planned chapters, executed strictly in order
- Decimal phases: reserved for urgent insertions and do not replace a chapter

- [x] **Phase 1: s01 Agent Loop** - 建立可注入、可离线验证的模型与工具结果循环
- [x] **Phase 2: s02 Tool Use** - 用工具处理器映射把单一 Bash 扩展为多个工具
- [x] **Phase 3: s03 Permission** - 在执行前落实 deny、ask、allow 权限决策
- [x] **Phase 4: s04 Hooks** - 用有序生命周期 Hook 扩展既有循环和权限语义
- [x] **Phase 5: s05 TodoWrite** - 用会话内 TODO 状态组织当前注意力
- [x] **Phase 6: s06 Subagent** - 在受限新上下文中执行子 Agent 并返回摘要
- [x] **Phase 7: s07 Skill Loading** - 发现技能清单并按需安全加载完整内容
- [x] **Phase 8: s08 Context Compact** - 压缩上下文且保留协议对与继续执行状态
- [x] **Phase 9: s09 Memory** - 筛选、持久化并按相关性恢复可信记忆
- [ ] **Phase 10: s10 System Prompt** - 由运行状态确定性组装并刷新 System Prompt
- [ ] **Phase 11: s11 Error Recovery** - 对模型边界错误执行有界、可解释的恢复
- [ ] **Phase 12: s12 Task System** - 管理可恢复、带依赖和所有权的持久任务
- [ ] **Phase 13: s13 Background Tasks** - 异步执行任务并由单一写入者注入完成通知
- [ ] **Phase 14: s14 Cron Scheduler** - 用可控时钟可靠创建、取消和恢复计划任务
- [ ] **Phase 15: s15 Agent Teams** - 以稳定身份、受限能力和邮箱组织 Agent Team
- [ ] **Phase 16: s16 Team Protocols** - 用相关联的结构化协议完成团队请求与关闭
- [ ] **Phase 17: s17 Autonomous Agents** - 运行自主状态循环并原子认领可执行任务
- [ ] **Phase 18: s18 Worktree Isolation** - 将任务绑定到可安全管理的 Git Worktree
- [ ] **Phase 19: s19 MCP Plugin** - 发现并适配经过本地边界的模拟 MCP 动态工具
- [ ] **Phase 20: s20 Comprehensive** - 证明全部机制围绕同一循环协作并完成学习证据审计

## Phase Details

### Phase 1: s01 Agent Loop
**Goal**: 学习者可以运行并解释完整的模型调用、工具请求、工具结果回传与最终响应终止循环
**Mode:** mvp
**Depends on**: Nothing (s00 baseline exists)
**Requirements**: LOOP-01
**Success Criteria** (what must be TRUE):
  1. 学习者可用脚本化模型客户端运行 `user → assistant(tool_use) → user(tool_result) → assistant(final)` 完整轨迹。
  2. 多工具调用、工具失败和最终响应都保留正确顺序与关联 ID，最终响应后不再发起模型调用。
  3. 稳定 CLI 可在临时工作区运行脱敏演示，离线测试同时证明模型 seam 与终止条件。
  4. s01 的增量、测试/演示、反思、单一提交、`s01-*` 标签和飞书子文档形成可复习闭环。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s01-agent-loop/`

### Phase 2: s02 Tool Use
**Goal**: 学习者可以在不改变 Agent Loop 主体结构的前提下，通过 `TOOL_HANDLERS` 映射调用 Bash、读、写、编辑和 Glob 工具
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: TOOL-01
**Success Criteria** (what must be TRUE):
  1. 在保留 Bash 的基础上新增 `read_file`、`write_file`、`edit_file` 和 `glob`，其参数与结果行为不超过上游 s02 `code.py`。
  2. Agent Loop 通过简单的 `TOOL_HANDLERS` 名称查找完成分发；未知名称返回 `Unknown: <name>`，不引入注册器类、统一错误模型或后续章节机制。
  3. `safe_path`、文件工具、Glob 和已有 Bash 的行为与上游 s02 教学范围一致，离线回归证明 s01 循环仍成立。
  4. s02 在 PyCharm diff 审查、讨论和个人反思确认后，以一个 `s02-*` 提交/标签及一个简洁飞书子文档结束。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s02-tool-use/`

### Phase 3: s03 Permission
**Goal**: 学习者可以区分 deny、ask、allow 并确认未授权工具永不执行
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: SAFE-01
**Success Criteria** (what must be TRUE):
  1. 同一工具调用在 deny、ask、allow 三种决策下产生清晰、可观察且可关联的结果。
  2. 测试证明 deny 不提示也不执行，ask 未获批准不执行，批准只作用于当前调用。
  3. 学习者能通过演示解释权限策略与操作系统沙箱的区别，s01-s02 回归保持通过。
  4. s03 在反思后以一个 `s03-*` 提交/标签和一个含验证证据的飞书子文档结束。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s03-permission/`

### Phase 4: s04 Hooks
**Goal**: 学习者可以用有序生命周期 Hooks 扩展循环而不改变既有权限与协议语义
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: HOOK-01
**Success Criteria** (what must be TRUE):
  1. UserPromptSubmit、PreToolUse、PostToolUse 和 Stop Hook 按可预测顺序运行并可被观察。
  2. 阻断、Hook 异常、PostToolUse 恰好一次和 Stop 有界继续均有离线失败路径测试。
  3. 权限继续通过统一执行 seam 生效，前序工具与循环回归通过。
  4. s04 的反思、单一 `s04-*` 提交/标签和飞书子文档记录 Hook 次序及边界。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s04-hooks/`

### Phase 5: s05 TodoWrite
**Goal**: 学习者可以用仅限当前会话的 TODO 状态组织注意力并与持久任务区分
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: TODO-01
**Success Criteria** (what must be TRUE):
  1. 学习者可创建、更新、完成并查看经过校验的会话内 TODO 列表。
  2. 新会话不会恢复旧 TODO，演示清楚说明它不是任务所有权或依赖系统。
  3. 无效状态和过度提醒有确定性处理，前序 Agent Loop 与 Hook 回归通过。
  4. s05 以反思、一个 `s05-*` 提交/标签和对应飞书子文档保存学习证据。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s05-todo-write/`

### Phase 6: s06 Subagent
**Goal**: 学习者可以在受限新上下文中运行 Subagent 并只向父 Agent 返回摘要
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: SUBA-01
**Success Criteria** (what must be TRUE):
  1. 父 Agent 可启动拥有新消息上下文、受限工具与独立执行边界的 Subagent。
  2. 轮数、递归深度和取消均有界，子 Agent 无法绕过父级工作区与权限约束。
  3. 父上下文只收到关联摘要而非完整子轨迹，离线测试证明前序循环未分叉。
  4. s06 的反思、一个 `s06-*` 提交/标签和飞书子文档记录隔离选择与上游简化点。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s06-subagent/`

### Phase 7: s07 Skill Loading
**Goal**: 学习者可以渐进发现技能并按需安全加载完整 SKILL.md
**Mode:** mvp
**Depends on**: Phase 6
**Requirements**: SKIL-01
**Success Criteria** (what must be TRUE):
  1. 学习者可查看精简技能目录，并只在选择某项后加载其完整 `SKILL.md`。
  2. 非法路径、不安全 YAML 和损坏清单被拒绝，加载文本不会被当作可信策略覆盖本地边界。
  3. 测试证明未选技能正文不会进入上下文，既有工具和 Subagent 契约保持通过。
  4. s07 以个人反思、一个 `s07-*` 提交/标签和证据完整的飞书子文档结束。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s07-skill-loading/`

### Phase 8: s08 Context Compact
**Goal**: 学习者可以压缩超限上下文且保留工具协议对、继续执行状态和溢出证据
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: CTXT-01
**Success Criteria** (what must be TRUE):
  1. 学习者可显式或在预算触发时压缩长对话，并继续完成原任务。
  2. assistant tool_use 与后续 user tool_result 始终作为不可分单元保留，必要状态与继续锚点不丢失。
  3. 溢出/归档证据可检查，重复压缩和摘要失败有界且由离线测试覆盖。
  4. s08 的反思、一个 `s08-*` 提交/标签和飞书子文档展示压缩前后行为证据。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s08-context-compact/`

### Phase 9: s09 Memory
**Goal**: 学习者可以安全持久化可信事实并在重启后按相关性恢复
**Mode:** mvp
**Depends on**: Phase 8
**Requirements**: MEM-01
**Success Criteria** (what must be TRUE):
  1. 经筛选事实写入可检查的持久记忆，并在新进程中按当前问题相关性重新加载。
  2. 秘密、不可信指令、猜测和任务不会被提升为记忆，重复事实可合并或更正。
  3. 演示可对比会话转录、压缩内容和持久记忆的不同生命周期，累计离线测试通过。
  4. s09 在反思后产出一个 `s09-*` 提交/标签和引用真实记忆证据的飞书子文档。
**Plans**: 1/1 complete — chapter evidence is recorded under `learning/s09-memory/`

### Phase 10: s10 System Prompt
**Goal**: 学习者可以由技能、记忆和运行状态确定性组装 System Prompt
**Mode:** mvp
**Depends on**: Phase 9
**Requirements**: PROM-01
**Success Criteria** (what must be TRUE):
  1. 相同输入状态生成顺序稳定且内容相同的 System Prompt，未适用的段落不会出现。
  2. 技能、记忆或运行状态变化会使缓存键变化并重新组装，状态本身仍由各自所有者管理。
  3. 测试与演示显示按需信息而非全部目录正文进入提示，前序上下文契约保持通过。
  4. s10 以反思、一个 `s10-*` 提交/标签和说明缓存失效证据的飞书子文档结束。
**Plans**: TBD

### Phase 11: s11 Error Recovery
**Goal**: 学习者可以对截断、溢出和模型错误执行类型明确且有界的恢复
**Mode:** mvp
**Depends on**: Phase 10
**Requirements**: RECV-01
**Success Criteria** (what must be TRUE):
  1. 输出截断可有界续写或提升 token 预算，上下文溢出可触发一次受控压缩重试。
  2. 暂时性错误使用可注入时钟/抖动进行有限退避，配置允许时可回退模型；不可重试错误立即明确失败。
  3. 离线故障测试证明无无限重试、无真实 sleep、无已执行工具副作用重复，累计回归通过。
  4. s11 的反思、一个 `s11-*` 提交/标签和飞书子文档记录恢复决策及退出结果。
**Plans**: TBD

### Phase 12: s12 Task System
**Goal**: 学习者可以创建、依赖、认领、完成和恢复文件持久化任务
**Mode:** mvp
**Depends on**: Phase 11
**Requirements**: TASK-01
**Success Criteria** (what must be TRUE):
  1. 学习者可创建带稳定 ID 和依赖的任务，合法认领/完成转换在重启后仍可恢复。
  2. 缺失依赖、循环、非法状态转换、所有权冲突和损坏记录不会被静默接受。
  3. 测试证明认领转换具备最小原子性，并能解释持久任务与 TodoWrite 的区别。
  4. s12 以反思、一个 `s12-*` 提交/标签和包含恢复/失败证据的飞书子文档结束。
**Plans**: TBD

### Phase 13: s13 Background Tasks
**Goal**: 学习者可以启动后台任务并由单一会话写入者恰好一次注入完成通知
**Mode:** mvp
**Depends on**: Phase 12
**Requirements**: BGND-01
**Success Criteria** (what must be TRUE):
  1. 启动后台任务立即返回稳定的 started 结果，前台 Agent Loop 可继续工作。
  2. Worker 只发布不可变完成记录，单一会话协调者恰好一次注入关联通知并拥有消息修改权。
  3. 使用事件而非真实 sleep 的测试覆盖成功、失败、重复交付和有界关闭，前序协议回归通过。
  4. s13 的反思、一个 `s13-*` 提交/标签和飞书子文档展示异步时序证据。
**Plans**: TBD

### Phase 14: s14 Cron Scheduler
**Goal**: 学习者可以用可控时钟创建、取消和恢复恰好触发一次的计划任务
**Mode:** mvp
**Depends on**: Phase 13
**Requirements**: CRON-01
**Success Criteria** (what must be TRUE):
  1. 学习者可创建会话型或持久计划任务、查看它们并在触发前取消。
  2. 可控时钟证明每个计划时刻只入队一次，重启恢复不会重复触发已记录时刻。
  3. Scheduler 不在锁内调用模型或修改消息，失败/关闭路径和后台任务回归可离线重现。
  4. s14 在反思后以一个 `s14-*` 提交/标签和记录 fake-clock 证据的飞书子文档结束。
**Plans**: TBD

### Phase 15: s15 Agent Teams
**Goal**: 学习者可以创建具有稳定身份、受限能力、邮箱传输和明确生命周期的 Agent Team
**Mode:** mvp
**Depends on**: Phase 14
**Requirements**: TEAM-01
**Success Criteria** (what must be TRUE):
  1. Lead 可创建稳定命名的 teammate，每个成员拥有明确工具/工作区能力和生命周期状态。
  2. 定向邮箱消息只被正确收件人消费并可由 lead 注入会话，成员不能获得未授予能力。
  3. 离线测试覆盖多收件人隔离、损坏/部分消息和有界关闭，并保留 Subagent/任务契约。
  4. s15 的反思、一个 `s15-*` 提交/标签和飞书子文档记录身份与传输边界。
**Plans**: TBD

### Phase 16: s16 Team Protocols
**Goal**: 学习者可以用带请求 ID 和预期响应类型的协议协调团队决策与关闭
**Mode:** mvp
**Depends on**: Phase 15
**Requirements**: PROT-01
**Success Criteria** (what must be TRUE):
  1. 计划评审、一般请求/响应和 shutdown 请求/确认使用可检查的类型化信封完成。
  2. request ID、预期响应类型和 pending 状态阻止错误、重复或过期响应推进协议。
  3. 离线轨迹证明审批不等于任务完成，结构化状态不依赖解析自由文本。
  4. s16 以反思、一个 `s16-*` 提交/标签和包含相关性证据的飞书子文档结束。
**Plans**: TBD

### Phase 17: s17 Autonomous Agents
**Goal**: 学习者可以运行 WORK、IDLE、SHUTDOWN 循环并原子认领合格任务
**Mode:** mvp
**Depends on**: Phase 16
**Requirements**: AUTO-01
**Success Criteria** (what must be TRUE):
  1. Teammate 能在 WORK、IDLE、SHUTDOWN 之间按可观察规则转换，并在空闲时响应控制消息。
  2. 两个 Agent 竞争同一任务时只有一个原子认领成功，依赖未满足的任务不会成为候选。
  3. 身份在压缩/恢复后保持，陈旧 owner、竞态和有界线程关闭由确定性测试覆盖。
  4. s17 在反思后产出一个 `s17-*` 提交/标签和记录竞态结果的飞书子文档。
**Plans**: TBD

### Phase 18: s18 Worktree Isolation
**Goal**: 学习者可以为任务创建、绑定和安全清理 Git Worktree 并理解隔离边界
**Mode:** mvp
**Depends on**: Phase 17
**Requirements**: WTRE-01
**Success Criteria** (what must be TRUE):
  1. 任务可绑定唯一分支、路径和显式 runtime cwd，并在临时 Git 仓库中完成可审计生命周期。
  2. dirty、locked、重复绑定或无效路径会拒绝默认清理，系统不通过直接删目录绕过 Git。
  3. 学习者可演示目录隔离并说明它不会自动解决语义/合并冲突，团队回归保持通过。
  4. s18 以反思、一个 `s18-*` 提交/标签和包含 Git 生命周期证据的飞书子文档结束。
**Plans**: TBD

### Phase 19: s19 MCP Plugin
**Goal**: 学习者可以发现、命名空间化并安全调用进程内模拟 MCP 动态工具
**Mode:** mvp
**Depends on**: Phase 18
**Requirements**: MCP-01
**Success Criteria** (what must be TRUE):
  1. 模拟 MCP 客户端可发现工具并以 `mcp__server__tool` 命名注册，同时保留内置工具。
  2. 名称冲突、不可信元数据、错误结果和调用失败都被规范化，动态工具继续经过本地权限与 dispatch 边界。
  3. 工具池变化使 prompt/registry 刷新，全部验证离线运行且不需要网络、凭据或真实 MCP transport。
  4. s19 的反思、一个 `s19-*` 提交/标签和飞书子文档明确说明模拟范围与 v2 边界。
**Plans**: TBD

### Phase 20: s20 Comprehensive
**Goal**: 学习者可以组合并解释 s01-s19 的机制，证明完整学习实现及证据链可运行、可追溯
**Mode:** mvp
**Depends on**: Phase 19
**Requirements**: COMP-01, EXPL-01, EVID-01, EVID-02, EVID-03, EVID-04, EVID-05, DOCS-01, DOCS-02, DOCS-03
**Success Criteria** (what must be TRUE):
  1. 一条安全、离线端到端轨迹组合循环、工具/权限、上下文/记忆、任务/并发、团队/Worktree 与 MCP，且 s01-s19 累计回归全部通过。
  2. 跨机制故障矩阵证明协议关联、单一消息写入者、有界恢复、权限传播、显式 cwd 和动态工具边界在组合后仍成立。
  3. 学习者可脱离教程用自己的语言解释各机制的控制流、状态生命周期、信任边界及相互关系。
  4. s01-s20 每章均有核对后的目标/增量、正向/失败/回归测试、安全演示、先于综合文档的个人观点、恰好一个聚焦提交和匹配标签。
  5. s20 飞书子文档完成后，父文档目录、状态和 20 个子文档入口齐全；每个子文档都引用真实代码路径、测试/演示、反思及不可变提交/标签证据。
**Plans**: TBD

## Progress

**Execution Order:** Phases execute strictly as 1 → 2 → 3 → … → 20.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. s01 Agent Loop | 1/1 | Complete | 2026-07-21 |
| 2. s02 Tool Use | 1/1 | Complete | 2026-07-21 |
| 3. s03 Permission | 1/1 | Complete | 2026-07-21 |
| 4. s04 Hooks | 1/1 | Complete | 2026-07-21 |
| 5. s05 TodoWrite | 1/1 | Complete | 2026-07-21 |
| 6. s06 Subagent | 1/1 | Complete | 2026-07-21 |
| 7. s07 Skill Loading | 1/1 | Complete | 2026-07-21 |
| 8. s08 Context Compact | 1/1 | Complete | 2026-07-22 |
| 9. s09 Memory | 1/1 | Complete | 2026-07-22 |
| 10. s10 System Prompt | 0/TBD | Not started | - |
| 11. s11 Error Recovery | 0/TBD | Not started | - |
| 12. s12 Task System | 0/TBD | Not started | - |
| 13. s13 Background Tasks | 0/TBD | Not started | - |
| 14. s14 Cron Scheduler | 0/TBD | Not started | - |
| 15. s15 Agent Teams | 0/TBD | Not started | - |
| 16. s16 Team Protocols | 0/TBD | Not started | - |
| 17. s17 Autonomous Agents | 0/TBD | Not started | - |
| 18. s18 Worktree Isolation | 0/TBD | Not started | - |
| 19. s19 MCP Plugin | 0/TBD | Not started | - |
| 20. s20 Comprehensive | 0/TBD | Not started | - |

---
*Roadmap created: 2026-07-19*
*Granularity: fine; learning contract fixes one chapter per phase*
