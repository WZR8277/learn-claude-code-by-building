# s02：Tool Use

## 本章要解决的问题

s01 的 Agent Loop 只认识一个 `bash` 工具，并在循环中硬编码
`run_bash(block.input["command"])`。s02 要证明：增加工具时，不需要给循环增加新的工具分支，只需定义工具并把 handler 放进分发表。

## 相比上一章的精确增量

严格跟随上游 s02，本章只增加：

- `safe_path()`；
- `run_read()`、`run_write()`、`run_edit()`、`run_glob()`；
- 从一个工具扩展到五个工具的 `TOOLS`；
- 工具名到处理函数的 `TOOL_HANDLERS` 字典；
- Agent Loop 中从硬编码 `run_bash()` 改为按名字查表并调用。

多工具调用仍按模型返回顺序执行。并发、权限、Hooks、通用注册表类、额外参数校验和更复杂的错误协议都不属于本章。

上游为了展示每章完整状态，把所有代码放在每章自己的 `code.py`。本项目按既定规则只维护一套持续演进实现，因此保留已有的 `cli.py`、`loop.py`、`tool.py` 模块拆分；这只改变文件组织，不增加运行功能。

## 保持不变的 s01 契约

- `while True` 模型—工具反馈循环；
- assistant 内容先加入消息历史；
- 每个结果继续使用原始 `tool_use_id`；
- `stop_reason` 不再是 `tool_use` 时结束本轮；
- bash 的基础危险字符串拦截、120 秒超时和输出截断。

## 核心数据流

```text
tool_use(name, input, id)
    ↓
handler = TOOL_HANDLERS.get(name)
    ↓
handler(**input) 或 Unknown: name
    ↓
tool_result(tool_use_id=id, content=output)
```

`TOOLS` 是给模型看的接口说明，`TOOL_HANDLERS` 是本地真正执行的函数。二者通过相同的工具名对应。

## 代码阅读顺序

1. `src/mini_claude_code/tool.py` 中四个新增工具函数。
2. 同一文件中的 `TOOLS` 和 `TOOL_HANDLERS`。
3. `src/mini_claude_code/loop.py` 中 handler 查找和调用的几行变化。
4. `tests/test_s02_tool_use.py` 中五工具、文件操作、路径边界和顺序分发测试。

## 验收状态

- [x] 五个工具定义均有同名 handler。
- [x] 读、写、编辑和 glob 行为与教程一致。
- [x] `safe_path()` 阻止工作区外路径。
- [x] 多工具调用保持原始顺序和关联 ID。
- [x] 未知工具作为工具结果返回模型。
- [x] s01 回归测试保持通过。
- [x] 学习者已审查 PyCharm diff 并记录个人观点。
- [x] 学习者已确认本章机制与范围。
- [x] 本章已形成单一 commit 和 `s02-*` tag。
- [x] 飞书子文档已创建并回填总目录。

## 本章阅读要点

- Agent Loop 从硬编码 Bash 改为按工具名查找 handler，因此新增工具不需要继续增加分支。
- `TOOLS` 提供给模型，`TOOL_HANDLERS` 负责本地执行；二者以工具名连接。
- `safe_path()` 检查解析后的真实路径，避免文件工具访问工作区之外。

`tool_use_id`、顺序执行以及后续章节的并发、权限和 Hooks 不作为本章额外讨论题。
