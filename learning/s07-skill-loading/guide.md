# s07：Skill Loading

## 本章要解决的问题

s06 已经可以把复杂子问题交给子 Agent，但项目知识和操作规范仍然没有按需进入上下文。如果把所有规范文档都塞进 system prompt，每一轮模型调用都会携带大量无关内容。

s07 新增 Skill Loading：启动时只把技能名称和一句话描述注入 system prompt；当模型判断需要完整说明时，再调用 `load_skill(name)` 加载对应 `SKILL.md`。

## 相比 s06 的精确增量

本章只增加：

- `skills/` 目录扫描；
- `SKILL.md` YAML frontmatter 中 `name`、`description` 的解析；
- `SKILL_REGISTRY` 注册表；
- `build_system()` 将技能目录注入 system prompt；
- `load_skill(name)` 工具按名称返回完整 `SKILL.md` 内容；
- 父 Agent 工具列表新增 `load_skill`。

它不是长期记忆，不是 system prompt 复杂组装器，不解析 `allowed-tools`、`paths`、`context: fork` 等真实 Claude Code 更复杂字段，也不加载远程/MCP/plugin 技能。

## 核心数据流

```text
启动时：
skills/*/SKILL.md
  -> parse name / description
  -> SKILL_REGISTRY
  -> build_system()
  -> system prompt 只出现技能目录

运行时：
assistant tool_use: load_skill(name)
  -> TOOL_HANDLERS["load_skill"]
  -> 完整 SKILL.md
  -> user tool_result
```

## diff 审查关注点

1. `build_system()` 是否只注入技能目录，而不是完整正文。
2. `load_skill(name)` 是否只按注册表查找，不把参数当路径读文件。
3. `load_skill` 是否仍是普通工具，通过 `TOOL_HANDLERS` 分发。
4. 子 Agent 是否没有获得 skill loading 能力，保持 s06 的受限边界。
5. 本章是否没有提前实现 s09 Memory 或 s10 System Prompt 的复杂状态组装。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s06-subagent`，当前应继续 `s07 Skill Loading`。
- [x] 已用本地上游副本比较 `s07_skill_loading` 与 `s06_subagent`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [ ] 最终测试、commit、tag 和飞书归档。
