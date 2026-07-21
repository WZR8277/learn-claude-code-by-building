# s06：Subagent

## 本章要解决的问题

s05 让模型能在当前会话内维护 TODO，但所有探索过程仍会进入父 Agent 的同一个 `messages[]`。当一个子问题需要读很多文件、跑多轮工具时，这些中间轨迹会污染父上下文。

s06 新增 `task` 工具：父 Agent 把复杂子问题交给一个同步子 Agent。子 Agent 拿到全新的 `messages[]` 独立运行，结束后只把最终文本摘要作为工具结果返回给父 Agent。

## 相比 s05 的精确增量

本章只增加：

- `task` 工具定义，并注册到父 Agent 的 `TOOL_HANDLERS`；
- `spawn_subagent(description)`，用全新的 `messages[]` 运行子 Agent；
- `SUB_SYSTEM` 等价提示：要求子 Agent 完成任务并返回简短摘要，不能继续委派；
- 子 Agent 只拿到 `bash`、`read_file`、`write_file`、`edit_file`、`glob`，不拿 `todo_write` 和 `task`；
- 子 Agent 工具调用仍触发 `PreToolUse` / `PostToolUse` Hook；
- 子 Agent 最多运行 30 轮，最终只返回文本摘要，不把完整子历史塞回父上下文。

它不是后台任务，不是持久任务系统，不是 Agent Team，也不涉及 worktree 隔离。

## 核心数据流

```text
父 Agent messages[]
  -> tool_use: task(description)
  -> spawn_subagent(description)
       -> 子 Agent messages[] = [{"role": "user", "content": description}]
       -> 子 Agent 自己循环调用基础工具
       -> 子 Agent 得到最终 text
  <- tool_result: "子 Agent 摘要"
父 Agent 继续用原 messages[] 工作
```

## diff 审查关注点

1. `task` 是否仍是普通工具，主循环没有为它写特殊分支。
2. 子 Agent 是否使用全新 `messages[]`，父上下文只收到摘要。
3. `SUB_TOOLS` 是否没有 `task`，避免递归委派。
4. 子 Agent 工具是否仍走 Hook，因此权限和日志边界不会被跳过。
5. 本章是否没有提前实现 s13 的后台任务、s15 的团队或 s18 的 worktree。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s05-todo-write`，当前应继续 `s06 Subagent`。
- [x] 已用本地上游副本比较 `s06_subagent` 与 `s05_todo_write`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
