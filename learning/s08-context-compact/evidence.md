# s08 Evidence

## Sync

- `git fetch --all --tags` completed.
- Latest local chapter tags after sync: `s01-agent-loop`, `s02-tool-use`, `s03-permission`, `s04-hooks`, `s05-todo-write`, `s06-subagent`, `s07-skill-loading`.
- Source of truth says s01-s07 are complete; next chapter is s08 Context Compact.
- Local upstream tutorial checkout used: `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main`.

## Upstream Delta

Compared local upstream `s08_context_compact/code.py` against `s07_skill_loading/code.py`.

Runtime delta implemented for local review:

- Add pre-call compaction pipeline in the parent Agent Loop.
- Add message snipping, micro compaction, large tool-result persistence, transcript writing, and summary-based compaction helpers.
- Add explicit `compact` tool as a loop-level tool without a normal `TOOL_HANDLERS` entry.
- Add one bounded reactive retry for prompt-too-long errors.
- Preserve `assistant tool_use` / `user tool_result` protocol pairs when compacting around tool calls.

## Automated Tests

```bash
conda run -n LearnClaudeCode pytest -q
```

Current local result before learner diff review:

```text
48 passed in 0.96s
```

Final local result before commit:

```text
48 passed in 1.05s
```
