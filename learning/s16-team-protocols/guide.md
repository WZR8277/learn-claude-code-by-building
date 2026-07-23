# s16：Team Protocols

## 本章要解决的问题

S15 让 Lead 和队友可以通过文件邮箱通信，但消息仍然偏松散：Lead 发一句话，队友回一句话，缺少请求、回复和状态之间的明确关联。

S16 新增的是结构化协议：一次请求有一个 `request_id`，回复必须带同一个 `request_id` 回来，Lead 再根据请求类型和回复类型更新状态。

## 相比 s15 的精确增量

本章只增加：

- `ProtocolState`：记录协议请求的 `request_id / type / sender / target / status / payload`；
- `pending_requests`：保存尚未完成的协议请求；
- `metadata`：消息体新增元数据，用来携带 `request_id` 和审批结果；
- `match_response()`：按 `request_id` 找请求，并校验响应类型是否匹配；
- `consume_lead_inbox()`：Lead 统一消费 inbox，先路由协议回复再返回消息；
- `request_shutdown`：Lead 发起体面关机请求；
- `submit_plan`：队友向 Lead 提交计划审批请求；
- `review_plan`：Lead 根据 `request_id` 审批或拒绝计划；
- 队友 idle loop：没有工具调用时不立刻退出，而是等待 inbox 中的新消息或关机请求。

本章没有实现真正的执行门控：队友提交计划后，是否等待批准再调用 `bash/write_file`，仍然依赖模型遵守协议。真实系统需要在工具派发层拦截未批准操作。

## 核心数据流

```text
Lead -> request_shutdown("alice")
  -> pending_requests[req_id] = shutdown/pending
  -> BUS.send("shutdown_request", metadata.request_id)

alice idle loop
  -> read inbox
  -> dispatch shutdown_request
  -> BUS.send("shutdown_response", metadata.request_id + approve)
  -> exit

Lead async wake/check_inbox
  -> consume_lead_inbox()
  -> match_response("shutdown_response", req_id)
  -> pending_requests[req_id].status = approved
```

关键点是：`request_id` 只是关联键，真正避免误更新的是 `match_response()` 里的类型校验。

## diff 审查关注点

1. `TeamMessage` 是否新增 `metadata`，并保持 JSONL 文件邮箱形式。
2. `ProtocolState` 和 `pending_requests` 是否只表达 S16 的 pending/approved/rejected 状态机。
3. `match_response()` 是否同时检查 `request_id` 和响应类型。
4. `consume_lead_inbox()` 是否成为 Lead 读取 inbox 的统一入口。
5. 队友 idle loop 是否能在 end_turn 后继续等消息，而不是直接退出。
6. 队友工具集是否只新增 `submit_plan`，没有提前实现 S17 自主认领任务。
7. 测试是否覆盖协议状态变化，而不是只测普通文本消息。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s15-agent-teams`，当前应继续 `s16 Team Protocols`。
- [x] 已用本地上游副本读取并对比 `s16_team_protocols`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [x] 最终测试通过。
- [ ] commit、tag 和飞书归档。
