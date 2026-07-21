# s06 Evidence

## Sync

- `git fetch --all --tags` completed.
- Latest local chapter tags after sync: `s01-agent-loop`, `s02-tool-use`, `s03-permission`, `s04-hooks`, `s05-todo-write`.
- Source of truth says s01-s05 are complete; next chapter is s06 Subagent.
- Local upstream tutorial checkout used: `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main`.

## Upstream Delta

Compared local upstream `s06_subagent/code.py` against `s05_todo_write/code.py`.

Runtime delta implemented for local review:

- Parent tool list adds `task`.
- `task` launches a synchronous subagent with fresh `messages[]`.
- Subagent gets only base tools: `bash`, `read_file`, `write_file`, `edit_file`, `glob`.
- Subagent tool dispatch still triggers `PreToolUse` and `PostToolUse`.
- Subagent has a bounded turn loop and returns only final text summary.

## Automated Tests

```bash
conda run -n LearnClaudeCode pytest -q
```

Current local result before learner diff review:

```text
32 passed in 0.89s
```

Final local result before commit:

```text
32 passed in 0.92s
```
