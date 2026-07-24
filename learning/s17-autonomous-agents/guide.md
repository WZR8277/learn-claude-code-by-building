# s17：Autonomous Agents

## 本章要解决的问题

S16 让 Lead 和队友之间有了结构化协议，但任务分配仍然依赖 Lead 主动发消息。只要任务板上有多个 pending 任务，Lead 就要一个个指派，队友不会自己找活。

S17 新增的是队友自治：队友完成一轮 WORK 后进入 IDLE，优先检查 inbox，再扫描任务板；如果发现 pending、无 owner、依赖已完成的任务，就自动 claim 并回到 WORK。

## 相比 s16 的精确增量

本章只增加：

- `scan_unclaimed_tasks()`：扫描可被认领的任务；
- `claim_task()` owner 检查：已有 owner 的任务不能被二次认领；
- 队友任务工具：`list_tasks / claim_task / complete_task`；
- `_idle_poll()`：空闲时按“inbox 优先、任务板其次、超时退出”工作；
- 队友生命周期：从 S16 的 WORK/等待消息，变成 WORK -> IDLE -> WORK/SHUTDOWN；
- 身份重注入：messages 过短时补一条 identity，避免简化压缩后队友忘记自己是谁；
- `spawn_teammate` 返回值标记为 autonomous，CLI 版本号更新到 S17。

本章没有实现文件锁、任务抢占、任务 release、真正的队友隔离或工作区隔离。这些属于后续章节或生产级实现。

## 核心数据流

```text
Lead -> create_task("写 API")
Lead -> spawn_teammate("alice")

alice WORK
  -> 模型没有工具调用，进入 IDLE

alice IDLE
  -> 先查 inbox：如果有 shutdown_request，回复并退出
  -> 没有 inbox，则 scan_unclaimed_tasks()
  -> claim_task(task_id, owner="alice")
  -> 把 <auto-claimed> 注入自己的 messages
  -> 回到 WORK

alice WORK
  -> 模型看到自己已认领任务
  -> 调用 read/write/bash/complete_task
  -> 完成后再次进入 IDLE 或最终超时退出
```

这里的关键不是“后台线程变聪明”，而是 harness 在队友 idle 时提供了一个找工作的固定入口。模型不需要 Lead 每次提醒，队友也不会一轮回答结束就死亡。

## diff 审查关注点

1. `claim_task()` 是否先拒绝已有 owner 的任务。
2. `scan_unclaimed_tasks()` 是否只返回 pending、无 owner、依赖已完成的任务。
3. 队友工具集是否从 5 个扩到 8 个，没有增加 Lead 新工具。
4. `_idle_poll()` 是否先处理 inbox，再扫描任务板。
5. idle 阶段收到 `shutdown_request` 是否仍能走 S16 的协议回复。
6. 自动 claim 成功后，是否把 `<auto-claimed>` 注入队友自己的 messages。
7. 队友线程退出前是否仍把 summary/result 发回 Lead。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s16-team-protocols`，当前应继续 `s17 Autonomous Agents`。
- [x] 已用本地上游副本读取并对比 `s17_autonomous_agents`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [x] 最终测试通过。
- [x] commit、tag 和飞书归档。
