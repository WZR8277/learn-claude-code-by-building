# s04：Hooks

## 本章要解决的问题

s03 的权限判断已经能保护工具执行，但它仍然是直接写在 Agent Loop 里的固定逻辑。s04 要把这些生命周期扩展点显式化：用户提交提示词、工具执行前、工具执行后、模型停止时，都可以触发按顺序注册的 Hook。

## 相比 s03 的精确增量

本章只增加：

- `HOOKS` 事件表；
- `register_hook(event, hook)`；
- `trigger_hooks(event, context)`；
- `UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop` 四个生命周期触发点；
- 示例 Hook：输入日志、工具调用日志、大输出提醒和停止摘要；
- 将 s03 的权限判断接入 `PreToolUse`，保持 handler 执行前阻断；
- Stop Hook 最多触发一次继续请求，避免停止阶段无限循环。

不引入配置文件、异步 Hook、插件发现、MCP、权限缓存或后续章节的任务系统。

## diff 审查关注点

1. `loop.py` 中权限判断是否仍发生在 handler 调用前。
2. `hooks.py` 是否只是一个有序 Hook 表，且第一个非空 Hook 结果会短路，而不是提前做复杂插件系统。
3. `PreToolUse` 返回内容时，工具是否不会执行，但仍返回关联 `tool_use_id` 的 `tool_result`。
4. `PostToolUse` 是否只在工具实际执行后触发一次。
5. `Stop` Hook 是否有次数上限，避免模型没有工具调用时无限自循环。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认远端最新章节标签为 `s03-permission`，当前应继续 `s04 Hooks`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者已完成本章学习并记录个人观点。
- [x] 学习者已确认进入最终测试、commit、tag 和飞书归档。
