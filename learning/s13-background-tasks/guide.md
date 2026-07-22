# s13：Background Tasks

## 本章要解决的问题

S12 的 Task System 解决的是“任务状态和依赖如何持久化”，但所有工具调用仍然同步执行。S13 关注慢工具调用：例如 `npm install`、`pytest`、`build` 这类命令可能跑很久，如果 Agent 一直等工具返回，主循环就被阻塞。

本章新增 Background Tasks：慢工具先返回一个占位 `tool_result`，真实执行放到后台线程；后台完成后，再把 `<task_notification>` 作为普通 text block 注入后续 user message。

## 相比 s12 的精确增量

本章只增加：

- `background.py`：后台任务状态、线程启动、结果收集；
- `bash.run_in_background` 参数：模型可以显式请求后台执行；
- `should_run_background()`：显式参数优先，慢命令关键词兜底；
- `start_background_task()`：为工具调用创建 `bg_0001` 这类后台任务 ID；
- `collect_background_results()`：把完成结果转换成 `<task_notification>`；
- loop 接入：权限通过后，慢工具后台派发，快工具仍同步执行。

它不是 s14 Cron Scheduler：本章没有定时器、周期任务、任务恢复、停止后台任务或输出文件追踪。

## 核心数据流

```text
LLM tool_use: bash(run_in_background=true)
  -> PreToolUse Hook
  -> start_background_task
  -> 立即返回占位 tool_result
  -> 后台线程真实执行 bash
  -> collect_background_results
  -> 注入 <task_notification>
```

关键点是：原始 `tool_use_id` 只对应一次 `tool_result`。后台完成不是第二个 tool_result，而是一个独立通知，否则会破坏 Messages API 的工具调用配对语义。

## diff 审查关注点

1. `background.py` 是否只负责后台任务生命周期，不混进 loop 的其它职责。
2. `run_in_background` 是否只是给 loop 判断策略，`run_bash()` 本身不直接开线程。
3. `PreToolUse` 是否仍然在后台调度之前执行。
4. 后台任务启动后返回的是原始 `tool_use_id` 的占位结果。
5. 后台完成结果是否用 `<task_notification>` 注入，而不是复用原始 `tool_use_id`。
6. 测试是否避免真实慢命令，用 fake handler 验证不阻塞行为。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s12-task-system`，当前应继续 `s13 Background Tasks`。
- [x] 已用本地上游副本比较 `s13_background_tasks` 与 `s12_task_system`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [x] 最终测试通过。
- [x] commit、tag 和飞书归档。
