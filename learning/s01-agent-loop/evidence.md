# s01 Evidence

## Chapter

- Chapter: `s01-agent-loop`
- Requirement: `LOOP-01`
- Date: 2026-07-21

## Main Code Paths

- `src/mini_claude_code/cli.py`
- `src/mini_claude_code/loop.py`
- `src/mini_claude_code/tool.py`
- `tests/test_s01_agent_loop.py`

## Automated Tests

Command:

```bash
conda run -n LearnClaudeCode pytest -q
```

Result:

```text
4 passed in 0.80s
```

Coverage added in s01:

- Fake model client returns a `tool_use` block.
- Local tool runner result is appended as `tool_result`.
- `tool_result.tool_use_id` matches the original `tool_use.id`.
- The loop stops when the model response does not request a tool.
- Baseline CLI and package smoke tests still pass.

## Runtime Demonstration

Command:

```bash
printf 'q\n' | conda run -n LearnClaudeCode python -m mini_claude_code
```

Result:

```text
mini-claude-code s01: Agent Loop ready
query: >>
```

The demo starts the CLI, displays the s01 prompt, receives `q`, and exits cleanly without invoking the live model API.

## Live Model Boundary

The implementation can call an Anthropic-compatible provider through:

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `MODEL_ID`

These values are loaded from `.env`, which is gitignored. No key is recorded in this evidence file.

## Commit And Tag

- Commit: final s01 commit in this repository.
- Tag: `s01-agent-loop`.

## Feishu

- Parent wiki depends on environment:
  - Home: `https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng`
  - Company: `https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc`
- Child document: pending until commit and tag exist.
- Before updating Feishu, ask whether the user is at home or company.
