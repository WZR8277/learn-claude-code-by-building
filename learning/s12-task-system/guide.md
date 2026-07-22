# s12：Task System

## 本章要解决的问题

s05 的 TodoWrite 只是当前会话里的执行清单，不能表达跨会话恢复、任务依赖或任务认领。S12 新增 Task System：每个任务持久化为 `.tasks/{id}.json`，任务之间用 `blockedBy` 表示上游依赖。

本章重点是“任务状态图”，不是后台任务。任务仍然由当前 Agent Loop 同步调用工具推进，S13 才会进入慢任务后台执行。

## 相比 s11 的精确增量

本章只增加：

- `Task` 数据结构：`id / subject / description / status / owner / blockedBy`；
- `.tasks/` 文件持久化；
- `create_task()`、`list_tasks()`、`get_task()`；
- `claim_task()`：`pending -> in_progress`，并写入 owner；
- `complete_task()`：`in_progress -> completed`，并报告被解锁的下游任务；
- 5 个工具：`create_task`、`list_tasks`、`get_task`、`claim_task`、`complete_task`。

它不是 s13 Background Tasks：本章不做异步 worker、后台通知、队列或单写入者事件注入。

## 核心数据流

```text
create_task
  -> 写入 .tasks/task_xxx.json
  -> status = pending

claim_task
  -> 检查 blockedBy 是否全部 completed
  -> pending -> in_progress
  -> owner = agent

complete_task
  -> in_progress -> completed
  -> 扫描 pending 任务
  -> 报告 now unblocked 的任务
```

## diff 审查关注点

1. `task_system.py` 是否把任务持久化、依赖检查和状态机集中管理。
2. `.gitignore` 是否忽略 `.tasks/`，避免演示任务文件进入 Git。
3. `tool.py` 是否只新增 5 个任务工具，没有提前引入后台任务机制。
4. 缺失依赖是否被视为 blocked，而不是忽略。
5. 注释是否说明 TodoWrite 与 Task System 的边界。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s11-error-recovery`，当前应继续 `s12 Task System`。
- [x] 已用本地上游副本比较 `s12_task_system` 与 `s11_error_recovery`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
