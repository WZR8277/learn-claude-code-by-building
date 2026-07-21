# s09 Evidence

## Sync

- `git fetch --all --tags` completed.
- Latest local chapter tags after sync: `s01-agent-loop`, `s02-tool-use`, `s03-permission`, `s04-hooks`, `s05-todo-write`, `s06-subagent`, `s07-skill-loading`, `s08-context-compact`.
- Source of truth says s01-s08 are complete; next chapter is s09 Memory.
- Local upstream tutorial checkout used: `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main`.

## Upstream Delta

Compared local upstream `s09_memory/code.py` against `s08_context_compact/code.py`.

Runtime delta implemented for local review:

- Add `.memory/` Markdown memory files with YAML frontmatter.
- Add `MEMORY.md` lightweight index and inject it into the system prompt.
- Select relevant memories by model side-query, with keyword fallback.
- Inject full selected memory content into the current user request only.
- Extract new memories after the loop reaches a final stop.
- Consolidate memory files when the threshold is reached.

## Automated Tests

```bash
conda run -n LearnClaudeCode pytest -q
```

Current local result before learner diff review:

```text
57 passed in 0.97s
```

Final local result before commit:

```text
57 passed in 0.97s
```
