# s15：Agent Teams

## 本章要解决的问题

S06 的 subagent 是一次性工具：Lead 把问题交出去，只等一个最终结论。S15 新增 Agent Team：Lead 可以启动有名字、有角色、有独立上下文的队友线程，并通过文件收件箱异步通信。

本章重点不是生产级多 Agent 编排，而是理解三件事：

- 队友有自己的 `messages`，不会直接污染 Lead 的上下文；
- 信息共享通过 MessageBus 完成，每个 Agent 一个 `.jsonl` 收件箱；
- Lead 收到队友结果后，把 inbox 内容注入为新的 user message，再继续一轮 Agent Loop。

## 相比 s14 的精确增量

本章只增加：

- `MessageBus`：基于 `.mailboxes/*.jsonl` 的文件收件箱；
- `TeamMessage`：落盘消息结构，包含发送方、接收方、内容、类型和时间；
- `spawn_teammate_thread()`：启动队友后台线程；
- 队友简化 Agent Loop：只允许 `bash/read_file/write_file/send_message`；
- `spawn_teammate`、`send_message`、`check_inbox` 三个 Lead 工具；
- CLI 异步唤醒：Lead 的 inbox 或后台任务结果到达时自动跑一轮；
- `.mailboxes/` 加入忽略列表，避免把运行时邮箱提交到仓库。

本章没有实现权限冒泡、队友关机协议、消息类型枚举、空闲长轮询或团队级任务协议。这些属于后续章节或真实 Claude Code 的更完整工程化设计。

## 核心数据流

```text
Lead -> spawn_teammate(name, role, prompt)
  -> teammate daemon thread
  -> teammate own messages + limited tools
  -> BUS.send(teammate, "lead", summary, "result")
  -> .mailboxes/lead.jsonl

CLI async poller
  -> BUS.peek("lead")
  -> BUS.read_inbox("lead")
  -> history.append("[Inbox] ...")
  -> agent_loop(history)
```

关键点是：队友线程不直接改 Lead 的 `history`。它只写 Lead 的邮箱；真正把消息注入历史的仍然是 Lead 侧的唤醒流程。

## diff 审查关注点

1. `team.py` 是否把邮箱协议、队友线程和格式化注入逻辑集中管理。
2. 队友 loop 是否有独立 `messages`，并且每轮先读自己的 inbox。
3. 队友工具集是否保持简化，没有提前拿到 cron、task、memory 等后续复杂能力。
4. `tool.py` 是否只增加三个 Lead 工具，并用现有文件和 shell handler 作为队友基础能力。
5. `cli.py` 的异步唤醒是否继续复用 `agent_lock`，避免多线程同时写同一份 history。
6. `.mailboxes/` 是否作为运行时产物被忽略。
7. 测试是否避免真实模型调用，只验证协议、注册和 loop 分发。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s14-cron-scheduler`，当前应继续 `s15 Agent Teams`。
- [x] 已用本地上游副本读取 `s15_agent_teams`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [ ] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [ ] 学习者完成本章个人观点。
- [ ] 最终测试通过。
- [ ] commit、tag 和飞书归档。
