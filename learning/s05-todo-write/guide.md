# s05：TodoWrite

## 本章要解决的问题

s04 已经把横切逻辑挂到 Hook 上，但模型在多步任务中仍可能直接开始执行。s05 新增 `todo_write` 工具，让模型先把当前会话内的步骤显式列出来，并在执行过程中更新状态。

## 相比 s04 的精确增量

本章只增加：

- `todo_write` 工具定义；
- `run_todo_write()` 与会话内 `CURRENT_TODOS`；
- TODO 输入归一化与教学版错误提示；
- 系统提示中加入“多步任务先计划，过程中更新状态”；
- Agent Loop 中的 `rounds_since_todo` 计数；
- 连续 3 轮工具调用没有更新 TODO 时注入 `<reminder>Update your todos.</reminder>`。

它不是持久任务系统，不跨进程恢复，不包含依赖、认领、所有权、后台执行或调度。

## diff 审查关注点

1. `todo_write` 是否只是普通工具，通过 `TOOL_HANDLERS` 自动分发，而不是改 Agent Loop 分支。
2. `CURRENT_TODOS` 是否只保存在当前进程内，没有落盘。
3. TODO 的状态是否只允许 `pending`、`in_progress`、`completed`。
4. reminder 是否只在多轮未更新 TODO 后注入，且 `todo_write` 调用后会重置计数。
5. s05 是否没有提前实现后续的 Task System。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认远端最新章节标签为 `s04-hooks`，当前应继续 `s05 TodoWrite`。
- [x] 已用本地上游副本比较 `s05_todo_write` 与 `s04_hooks`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者已完成本章学习并记录个人观点。
- [x] 学习者已确认进入最终测试、commit、tag 和飞书归档。
