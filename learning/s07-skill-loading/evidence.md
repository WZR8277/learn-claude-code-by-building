# s07 Evidence

## Sync

- `git fetch --all --tags` completed.
- Latest local chapter tags after sync: `s01-agent-loop`, `s02-tool-use`, `s03-permission`, `s04-hooks`, `s05-todo-write`, `s06-subagent`.
- Source of truth says s01-s06 are complete; next chapter is s07 Skill Loading.
- Local upstream tutorial checkout used: `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main`.

## Upstream Delta

Compared local upstream `s07_skill_loading/code.py` against `s06_subagent/code.py`.

Runtime delta implemented for local review:

- Scan local `skills/` directories for `SKILL.md`.
- Parse `name` and `description` from YAML frontmatter.
- Inject skill catalog into system prompt through `build_system()`.
- Register `load_skill(name)` as a normal parent Agent tool.
- Return full `SKILL.md` content only when `load_skill` is called.

## Automated Tests

```bash
conda run -n LearnClaudeCode pytest -q
```

Current local result before learner diff review:

```text
39 passed in 1.50s
```

Final local result before commit:

```text
39 passed in 0.96s
```
