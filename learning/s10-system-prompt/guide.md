# s10：System Prompt

## 本章要解决的问题

s01 到 s09 的 system prompt 还是一个相对固定的字符串。随着工具、技能、记忆等运行态越来越多，把所有说明都硬塞在同一段 prompt 里，会让修改边界变模糊，也无法表达“某些内容只有在真实存在时才加载”。

s10 新增的是运行时 prompt 组装：把 prompt 拆成稳定 section，根据当前工作目录、可用工具、技能目录和记忆索引拼接，并用确定性 context key 缓存结果。

## 相比 s09 的精确增量

本章只增加：

- `PROMPT_SECTIONS`：把身份、工具、工作区、技能和记忆拆成独立 section；
- `update_prompt_context()`：从真实运行态派生 prompt context；
- `assemble_system_prompt()`：按稳定顺序拼接 section；
- `get_system_prompt()`：用 `json.dumps(..., sort_keys=True)` 做进程内缓存；
- Agent Loop 在工具结果回传后重新计算 prompt context 和 system prompt。

它不是 s11 Error Recovery，也不是任务系统。prompt cache 也只是本地字符串组装缓存，不等于真实 API prompt cache。

## 核心数据流

```text
当前运行态
  -> workspace / enabled_tools / skill_catalog / memory_index
  -> update_prompt_context()
  -> get_system_prompt()
  -> client.messages.create(system=...)

工具执行后
  -> 重新读取真实运行态
  -> 如 MEMORY.md 或工具集合变化，重新组装 system prompt
```

## diff 审查关注点

1. `system_prompt.py` 是否只负责 section、context 和缓存。
2. `loop.py` 是否从固定 `build_system()` 改成 `update_prompt_context()` + `get_system_prompt()`。
3. 记忆正文仍然只按需注入当前 user turn，`memory_index` 才进入 system prompt。
4. 缓存 key 是否基于确定性 JSON，而不是 Python `hash()`。
5. 代码是否没有提前引入 s11 的错误恢复、s12 的任务系统或真实 API prompt cache。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s09-memory`，当前应继续 `s10 System Prompt`。
- [x] 已用本地上游副本比较 `s10_system_prompt` 与 `s09_memory`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
