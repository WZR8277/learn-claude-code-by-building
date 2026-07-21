# s08：Context Compact

## 本章要解决的问题

s07 已经能按需加载 skill，但 Agent Loop 的消息历史仍会随着多轮工具调用持续膨胀。上下文一旦超过模型限制，后续调用会失败；即使没失败，过长的旧工具输出也会挤占当前任务空间。

s08 新增 Context Compact：在模型调用前主动压缩消息历史，在溢出错误后做一次响应式压缩，并提供显式 `compact` 工具让模型主动要求“把前文总结后继续”。

## 相比 s07 的精确增量

本章只增加：

- 上下文大小估算 `estimate_size()`；
- 长消息历史的中段裁剪 `snip_compact()`；
- 旧工具结果的微压缩 `micro_compact()`；
- 大工具输出落盘 `tool_result_budget()` / `persist_large_output()`；
- 对话转录归档 `write_transcript()`；
- LLM 摘要式压缩 `compact_history()`；
- prompt 过长后的单次响应式压缩 `reactive_compact()`；
- `compact` 工具声明，以及 Agent Loop 对它的内置处理。

它不是 s09 Memory：压缩摘要仍然属于当前会话延续，不会把事实筛选为长期记忆，也不会跨进程检索恢复。

## 核心数据流

```text
每轮模型调用前：
messages
  -> tool_result_budget()
  -> snip_compact()
  -> micro_compact()
  -> 超过 CONTEXT_LIMIT 时 compact_history()
  -> client.messages.create(...)

模型请求 compact 工具时：
assistant tool_use: compact
  -> compact_history(messages)
  -> 保留本轮 compact tool_use / tool_result 协议对
  -> 下一轮继续

模型报 prompt_too_long 时：
exception
  -> reactive_compact(messages)
  -> 最多重试一次
```

## diff 审查关注点

1. `compact.py` 是否只处理当前会话压缩，没有提前做长期记忆。
2. `snip_compact()` / `reactive_compact()` 是否避免拆散 `assistant tool_use -> user tool_result`。
3. `compact` 是否是 loop 内置工具，而不是普通 `TOOL_HANDLERS` handler。
4. `loop.py` 是否在每次模型调用前执行压缩预算。
5. prompt 过长后的响应式压缩是否有界，避免无限重试。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s07-skill-loading`，当前应继续 `s08 Context Compact`。
- [x] 已用本地上游副本比较 `s08_context_compact` 与 `s07_skill_loading`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
