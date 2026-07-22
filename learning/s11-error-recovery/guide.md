# s11：Error Recovery

## 本章要解决的问题

到 s10 为止，Agent Loop 已经能组装 prompt、调用工具、压缩上下文、加载记忆，但模型调用失败时仍然很脆弱。真实 API 使用里，输出被截断、上下文超限、429 限流、529 过载都不是罕见异常。

s11 新增的是有界错误恢复：根据错误类型选择不同恢复路径，恢复后回到 loop 重新调用模型；无法恢复时给出明确错误并退出，而不是无限重试或直接崩溃。

## 相比 s10 的精确增量

本章只增加：

- `RecoveryState` 记录输出扩容、续写、响应式压缩和 529 连续次数；
- `with_retry()` 对 429/529 做指数退避和有界重试；
- 连续 529 后可切换 `FALLBACK_MODEL_ID`；
- `is_prompt_too_long_error()` 识别 prompt/context 超限错误；
- `max_tokens` stop reason 先升级输出预算，再用续写提示继续；
- prompt 太长时只做一次 reactive compact，再失败则明确退出。

它不是 s12 Task System：本章不引入持久任务、依赖图、后台执行或多 Agent 协作。

## 核心数据流

```text
模型调用
  -> with_retry()
    -> 429/529: 指数退避，必要时切备用模型
    -> 其它异常交回外层

外层异常
  -> prompt_too_long: reactive_compact 一次后重试
  -> 仍失败或不可恢复: 写入错误消息并退出

正常响应
  -> stop_reason == max_tokens
    -> 首次：提高 max_tokens，原请求重试
    -> 后续：保存截断输出，追加续写提示，最多 3 次
```

## diff 审查关注点

1. `error_recovery.py` 是否只负责错误分类、恢复状态、退避和重试。
2. `loop.py` 是否把模型调用包进 `with_retry()`，而不是让工具或 hook 重复执行。
3. 首次 `max_tokens` 是否不把截断响应写进 `messages`，避免污染历史。
4. prompt too long 是否只触发一次 reactive compact，避免空转。
5. 429/529 测试是否使用假 sleep，不让测试真的等待。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s10-system-prompt`，当前应继续 `s11 Error Recovery`。
- [x] 已用本地上游副本比较 `s11_error_recovery` 与 `s10_system_prompt`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
