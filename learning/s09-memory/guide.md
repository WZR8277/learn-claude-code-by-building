# s09：Memory

## 本章要解决的问题

s08 的 Context Compact 可以让当前会话在上下文变长时继续运行，但压缩摘要是有损的，而且新开会话后摘要也不存在。用户偏好、项目事实、反复反馈这类信息如果只留在对话里，很容易在压缩或跨电脑学习时丢掉。

s09 新增 Memory：用 `.memory/` 目录保存跨会话仍然有用的知识。`MEMORY.md` 只作为轻量索引进入 system prompt，具体记忆文件按当前请求相关性临时注入；回合结束后再从对话中提取新记忆。

## 相比 s08 的精确增量

本章只增加：

- `.memory/` 目录和 `MEMORY.md` 索引；
- 单条记忆文件的 Markdown + YAML frontmatter 格式；
- `write_memory_file()` 写入记忆并重建索引；
- `read_memory_index()` 把记忆目录注入 system prompt；
- `select_relevant_memories()` 根据最近对话选择相关记忆；
- `load_memories()` 把完整记忆内容包进当前 user turn；
- `extract_memories()` 在最终停止后提取新偏好、约束或项目事实；
- `consolidate_memories()` 在文件数达到阈值时整理去重。

它不是 s10 System Prompt：本章只是在现有 system prompt 中追加记忆索引，不做分段 prompt 组装、缓存键或运行时 prompt 框架。

## 核心数据流

```text
用户新请求开始：
.memory/MEMORY.md
  -> build_system(..., memory_index)

最近对话 + 记忆目录
  -> select_relevant_memories()
  -> read selected .memory/*.md
  -> 注入当前 user turn

Agent Loop 结束：
pre_compress messages
  -> extract_memories()
  -> write_memory_file()
  -> rebuild MEMORY.md
  -> consolidate_memories() if threshold reached
```

## diff 审查关注点

1. `memory.py` 是否把索引和完整记忆分开，避免 system prompt 常驻完整正文。
2. `loop.py` 是否在模型调用前注入相关记忆，但不修改真实 `messages` 历史。
3. 记忆提取是否发生在最终停止后，并使用压缩前快照。
4. 记忆写入是否只覆盖本章范围，没有引入任务系统、权限冒泡或 prompt 组装框架。
5. S07 skill loading、S08 compact、S04 hooks 等前序机制是否仍保留。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s08-context-compact`，当前应继续 `s09 Memory`。
- [x] 已用本地上游副本比较 `s09_memory` 与 `s08_context_compact`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
