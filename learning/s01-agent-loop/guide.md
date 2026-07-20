# s01: Agent Loop

## 本章要解决的问题

s01 建立最小可运行 Agent Loop：模型可以请求工具，本地 harness 执行工具，并把工具结果带着原始 `tool_use.id` 回传给模型，直到模型不再请求工具为止。

## 相比上一章的增量

s00 只有包结构、CLI 入口和 smoke tests。s01 新增：

- 交互式 CLI 输入循环。
- Anthropic 兼容模型客户端调用。
- 一个最小 `bash` 工具定义和执行函数。
- `assistant(tool_use) -> user(tool_result) -> assistant(final)` 的循环协议。
- 可注入 fake client 的离线测试 seam。

## 核心数据流

```text
user message
-> client.messages.create(...)
-> assistant content blocks
-> if stop_reason == "tool_use": run local tool
-> append user tool_result with matching tool_use_id
-> call model again
-> if stop_reason != "tool_use": return to CLI
```

## 代码阅读顺序

1. `src/mini_claude_code/cli.py`
2. `src/mini_claude_code/loop.py`
3. `src/mini_claude_code/tool.py`
4. `tests/test_s01_agent_loop.py`

## 实现任务

- [x] 加载 `.env` 中的模型配置，并在自定义 base URL 时清理可能冲突的 `ANTHROPIC_AUTH_TOKEN`。
- [x] 建立 CLI 历史消息列表，把用户输入追加为 `{"role": "user", "content": ...}`。
- [x] 调用模型并把 assistant content blocks 追加回历史。
- [x] 识别 `tool_use` block，执行本地 `bash` 工具。
- [x] 使用 `block.id` 生成匹配的 `tool_result.tool_use_id`。
- [x] 在没有工具调用时终止本轮 Agent Loop。
- [x] 使用 fake client 覆盖工具调用和无工具终止路径。

## 验收标准

- [x] 自动化测试通过。
- [x] 安全的运行演示通过。
- [x] 个人观点已经记录。
- [ ] 本章已形成单一 commit 和 tag。
- [ ] 飞书子文档已创建并回填总目录。

## 思考题

1. Claude tool loop 和传统 ReAct 的关系是什么？
2. 为什么 `tool_result` 必须带回 `tool_use_id`？
3. 为什么 `stop_reason != "tool_use"` 可以作为 s01 的终止条件？
4. 为什么模型不需要工具时不应该由 harness 自动反复调用模型“继续思考”？
