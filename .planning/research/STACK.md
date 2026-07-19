# Stack Research

**Domain:** Chapter-by-chapter Python reconstruction of an educational coding-agent harness
**Project:** Learn Claude Code by Building
**Researched:** 2026-07-19
**Confidence:** MEDIUM (primary sources were cross-checked, but both upstream and package behavior remain time-sensitive)

## Recommendation in One Sentence

Keep the existing Python 3.11+ `src/mini_claude_code` package and its plain synchronous Anthropic Messages API loop; standardize on a deliberately small, bounded dependency set (`anthropic`, `python-dotenv`, PyYAML only when skills arrive, and pytest), with injected model clients, environment-backed configuration, deterministic offline tests, and no agent framework or production MCP SDK before the curriculum itself calls for one.

## Upstream Facts vs. Local Decisions

| Area | Upstream fact (canonical root `s01`–`s20`) | Local 2026 decision | Learning/chapter reason |
|------|-------------------------------------------|---------------------|-------------------------|
| Python | Standalone Python scripts; upstream CI runs Python 3.11 | Preserve `requires-python = ">=3.11"`; test the floor and a current interpreter | Avoid language/toolchain migration while verifying the stated compatibility floor |
| Model API | Every chapter uses synchronous `Anthropic().messages.create(...)` | Use the same low-level synchronous Messages API behind a tiny injectable client boundary | The manual `stop_reason` / `tool_use` / `tool_result` loop is the subject of s01–s02 |
| Runtime dependencies | `anthropic>=0.25.0`, `python-dotenv>=1.0.0`, `pyyaml>=6.0` | Refresh to bounded, known-good 2026 ranges; do not add orchestration packages | Makes installs repeatable without replacing the upstream mechanisms being learned |
| YAML | Imported only by s07 and s20 | Keep PyYAML installed for the milestone, but do not use it before s07; always use `yaml.safe_load` | Preserves chapter causality and avoids unsafe object construction |
| Concurrency | Standard-library `threading`, `queue`, and subprocesses | Keep those primitives; test them with events and bounded joins | s13–s17 explicitly teach harness concurrency rather than an async framework |
| Persistence | Standard-library JSON/JSONL, files, dataclasses, and Git worktrees | Keep file-backed state under controlled workspace paths; no database | s09 and s12–s18 teach transparent persistence and coordination formats |
| MCP | s19 contains an in-process teaching `MCPClient` with mock servers; it does not use an MCP package or transport | Implement the same abstraction and mock discovery first; defer a real MCP SDK/transport to a post-s20 extension | Prevents transport/OAuth complexity from replacing the s19 lesson about tool-pool assembly |
| Tests | Upstream uses pytest as runner, mixes pytest parametrization with `unittest`, fakes imported modules, and runs `python -m pytest tests -q` | Standardize new tests on pytest fixtures while retaining existing unittest tests unchanged until touched | pytest runs unittest suites, so migration work adds no learning value |

## Recommended Stack

### Core Technologies

| Technology | Version/range | Purpose | Why recommended |
|------------|---------------|---------|-----------------|
| CPython | `>=3.11` | Runtime for the single evolving package | It is already the project contract and upstream CI baseline. Python 3.11 provides `tomllib`, modern typing, dataclasses, pathlib, threads, queues, and subprocess APIs needed by the course. Do not raise the floor during s01–s20. |
| Anthropic Python SDK | `>=0.117,<0.118` for the current milestone | Messages API, typed response blocks, provider client | PyPI lists 0.117.0 as current on 2026-07-19 and it supports Python 3.9+. A narrow minor range is intentional because the SDK is still `0.x`; upgrade deliberately between chapters only after the offline contract suite passes. |
| setuptools build backend | Preserve existing `setuptools.build_meta` and `setuptools>=68` | Builds the current `src`-layout package and console entry point | The package shell already works. Changing build backend or package manager has no chapter learning payoff. |
| pip + `venv` | Bundled/current with the chosen interpreter | Editable local install and isolated environment | Matches the repository README and requires no toolchain migration. Use `python -m pip`, never a bare interpreter-ambiguous `pip`. |

### Runtime Libraries

| Library | Version/range | Purpose | First chapter that needs it |
|---------|---------------|---------|-----------------------------|
| `anthropic` | `>=0.117,<0.118` | Low-level synchronous Messages API client | s01: agent loop |
| `python-dotenv` | `>=1.2.2,<2` | Load a gitignored local `.env` for interactive runs | s01: local provider configuration |
| `PyYAML` | `>=6.0.3,<7` | Parse skill frontmatter/manifests | s07: skill loading; again in s20 |

Everything else required by the canonical chapters is in the Python standard library: `ast`, `dataclasses`, `datetime`, `json`, `os`, `pathlib`, `queue`, `random`, `re`, `subprocess`, `threading`, and `time`. Optional `readline` behavior must remain guarded by `try/except ImportError` for cross-platform compatibility.

### Development and Testing Tools

| Tool | Version/range | Purpose | Standardized usage |
|------|---------------|---------|--------------------|
| pytest | `>=9.1,<10` | Unit, contract, CLI, and bounded integration tests | New tests use plain assertions, fixtures, and parametrization. Existing `unittest.TestCase` tests remain valid because pytest runs them natively. |
| `tmp_path` | built into pytest | Isolated workspace, task store, memory, transcripts, skills, and temporary Git repositories | Mandatory for filesystem-affecting tests from s02 onward; never point tests at the real checkout or home directory. |
| `monkeypatch` | built into pytest | Environment variables, current directory, client factories, subprocess runner, time, and random jitter | Prefer dependency injection first; use monkeypatch at external seams, not deep inside business logic. |
| `capsys` / `capfd` | built into pytest | CLI output and subprocess/file-descriptor output | Use `capsys` for Python output; `capfd` only where a subprocess or OS descriptor is genuinely involved. |
| `subprocess.run` with `sys.executable` | standard library | End-to-end CLI smoke tests | Invoke `sys.executable -m mini_claude_code` with explicit input, timeout, cwd, and sanitized environment. |
| GitHub Actions | upstream pins actions and tests Python 3.11 | Repeatable CI | Retain a 3.11 job as the compatibility gate; add one current-Python job only after local tests are deterministic. Never require API credentials for the default job. |

Do not add `pytest-mock`: `monkeypatch` plus small fakes are sufficient and keep the mocking model visible. Do not make coverage percentage a chapter completion criterion; require behavioral evidence for the mechanism introduced in that chapter instead.

## Chapter Dependency and Test Impact

| Chapters | Stack increment | Required test seam |
|----------|-----------------|--------------------|
| s01–s02 | `anthropic`, dotenv, subprocess/pathlib | Fake Messages API responses containing text and tool-use blocks; fake command runner; assert message ordering and multiple tool calls without network access |
| s03–s04 | No new dependency | Table-driven permission rules; hook ordering and failure isolation; destructive commands must never execute in tests |
| s05–s06 | Standard-library `ast`/JSON and injected recursive agent runner | Validate todo parsing without `eval`; give subagents fresh message lists and assert isolation |
| s07 | PyYAML begins | Parse temporary skill manifests with `yaml.safe_load`; reject malformed or traversal-prone paths |
| s08–s11 | Standard-library JSON/time/random; Anthropic error types | Preserve adjacent tool-use/tool-result pairs during compaction; inject clock/jitter; at s11 disable SDK retries so harness retry behavior is observable |
| s12 | dataclasses + JSON files | Atomic-ish task-state transitions in `tmp_path`; dependency graph and corrupted-file cases |
| s13–s17 | threading, queue, datetime | Use `threading.Event`, queues, and bounded joins instead of real sleeps; assert notification/mailbox protocols deterministically |
| s18 | Git CLI through subprocess | Create a temporary Git repository; skip with an explicit reason if Git is unavailable; validate path ownership and cleanup without touching the project worktree |
| s19 | In-process mock MCP abstraction only | Tool discovery, normalized names, collision behavior, schema translation, annotations, dispatch, and tool errors—all offline |
| s20 | All three runtime dependencies | Run the cross-mechanism contract suite plus a safe offline end-to-end trajectory; real-provider smoke test remains opt-in |

## Configuration Contract

### Environment variables

Standardize on the upstream-compatible names:

| Variable | Required | Policy |
|----------|----------|--------|
| `ANTHROPIC_API_KEY` | For live Anthropic calls | Never commit, print, persist in transcripts, or place in chapter/Feishu documentation. Let the SDK read it from the environment. |
| `MODEL_ID` | For live runs | Required and validated once at CLI startup; do not hardcode a model ID in source because availability changes. |
| `ANTHROPIC_BASE_URL` | Optional | Pass to the client only when non-empty. Treat non-Anthropic compatible providers as an explicit compatibility mode, not proof of semantic equivalence. |
| `FALLBACK_MODEL_ID` | Optional from s11 | Read only when error recovery is introduced. It must not silently replace the primary model during earlier chapters. |

Keep a checked-in `.env.example` with placeholders and comments, and keep `.env` ignored. Unlike upstream's educational scripts, call `load_dotenv(override=False)` locally: shell/CI-provided values should outrank a developer file. The upstream `override=True` is convenient for standalone demos but can silently replace an intentional environment value.

Create configuration at the CLI composition boundary and pass it inward. A small frozen dataclass is enough; do not add Pydantic Settings. Fail fast with a concise missing-variable error for live mode, but allow tests to construct configuration directly without secrets.

### Anthropic client policy

- Use `Anthropic(...)`, not `AsyncAnthropic`, through s20. Threads in s13–s17 are the lesson; mixing in an event loop would introduce a second concurrency model.
- Inject a client or a narrow `messages.create` protocol into the loop. Never make an import-time network call, and avoid a global client that tests must replace through `sys.modules` tricks.
- Set an explicit request timeout for interactive learning runs (recommended default: 120 seconds, configurable). The official SDK default is ten minutes, which is too long for a failed local exercise.
- The SDK retries connection failures, 408, 409, 429, and 5xx responses twice by default. Before s11, accepting that default is reasonable. In s11 and s20, construct the client with `max_retries=0` so the chapter's own exponential backoff, jitter, retry counts, and fallback model are not hidden or multiplied by SDK retries.
- Preserve the manual API contract: an assistant response containing `tool_use` must be followed immediately by a user message whose leading content blocks are the matching `tool_result` records. Tests should lock down this invariant because compaction and hooks can accidentally break it.
- Log request IDs and error categories, not prompts, API keys, full environment dictionaries, or unredacted tool results.

## Proposed `pyproject.toml` Standard

The next dependency-maintenance change should retain the current build and entry-point structure and narrow only the dependency ranges:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
requires-python = ">=3.11"
dependencies = [
  "anthropic>=0.117,<0.118",
  "python-dotenv>=1.2.2,<2",
  "pyyaml>=6.0.3,<7",
]

[project.optional-dependencies]
dev = ["pytest>=9.1,<10"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
markers = [
  "integration: requires external software or real provider credentials",
  "slow: bounded concurrency or worktree integration test",
]
```

Install with:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest
```

For reproducible chapter evidence, record the Python version, resolved package versions, test command, and model ID (never the key) in the chapter record. A lock/constraints file is useful for long-term replay, but adopting a new package manager is not required; defer that workflow decision until it can be made once for the whole repository rather than chapter by chapter.

## Alternatives Considered

| Recommended | Alternative | When the alternative would make sense |
|-------------|-------------|---------------------------------------|
| Low-level Anthropic SDK | Claude Agent SDK | After s20, when consuming a ready-made production agent runtime is the goal rather than learning how its harness mechanisms work |
| Synchronous client | `AsyncAnthropic` / asyncio | A post-course performance exercise involving many concurrent network requests; not while s13–s17 are teaching explicit threads and mailboxes |
| Standard-library dataclasses/files | Pydantic + database | A later productization milestone needing public validation schemas, migrations, concurrent writers, or operational querying |
| Mock MCP client in s19 | Official MCP Python SDK | A post-s19 extension that explicitly studies real stdio/HTTP transports, lifecycle, authentication, and server interoperability |
| pytest built-ins | pytest-mock and a large plugin suite | Only if repeated project-wide patterns demonstrate a real maintenance benefit |
| pip/setuptools | uv, Poetry, Hatch | A separate repository-tooling milestone; none improves understanding of agent loops, permissions, compaction, teams, or MCP assembly |

## What Not to Introduce During s01–s20

| Avoid | Why | Use instead |
|-------|-----|-------------|
| LangChain, LangGraph, AutoGen, CrewAI, or another agent framework | It would implement or hide the loop, dispatch, memory, task, and team mechanisms the learner is supposed to build | Plain Python plus the Anthropic Messages API |
| Claude Agent SDK | It supplies a higher-level agent runtime and collapses the learning surface | The base `anthropic` SDK and local harness code |
| A real MCP transport/runtime in s19 | Upstream s19 intentionally teaches discovery and pool assembly with mocks; transport/OAuth are explicitly outside its scope | In-process mock client and offline contract tests |
| asyncio mixed with threads | Two concurrency models make s13–s17 behavior and failure modes harder to explain | `threading`, `queue`, `Event`, and bounded joins |
| Database/Redis/message broker | Hides the educational JSON/JSONL/task/mailbox protocols and adds operational setup | pathlib, dataclasses, JSON, append-only JSONL |
| Docker as a prerequisite | Adds environment and filesystem indirection before worktree/path behavior is understood | Local virtual environment and temporary directories |
| `load_dotenv(override=True)` | A local file can unexpectedly override shell or CI settings | `load_dotenv(override=False)` and explicit startup validation |
| `eval` for todo, skill, task, or MCP inputs | Model/external input is untrusted and can execute arbitrary Python | `json.loads`, `ast.literal_eval` only where curriculum compatibility requires it, `yaml.safe_load`, and schema validation |
| Live API calls in default tests | Cost, nondeterminism, rate limits, credential leakage, and provider drift | Scripted fake responses; opt-in `integration` tests |
| Real `sleep`-driven concurrency tests | Slow and flaky; masks races | Events, queues, injected clock, bounded timeouts |

## Version Compatibility and Upgrade Policy

| Component | Verified current state on 2026-07-19 | Project policy |
|-----------|--------------------------------------|----------------|
| Python | Local floor is 3.11; upstream CI tests 3.11 | Keep 3.11 as mandatory gate through s20 |
| `anthropic` | 0.117.0; requires Python 3.9+ | Pin to the 0.117 minor line for this milestone; upgrade deliberately with the message/tool/error contract suite |
| pytest | 9.1.1; requires Python 3.10+ | Use 9.x; it remains compatible with Python 3.11 and runs existing unittest tests |
| python-dotenv | 1.2.2; requires Python 3.10+ | Use 1.2.x behavior; environment values win (`override=False`) |
| PyYAML | 6.0.3; requires Python 3.8+ | Use 6.x and only `safe_load` for project-controlled skill manifests |

Dependency freshness is not the same as learning progress. Do not bump packages inside a chapter implementation commit unless the chapter requires the bump. When upgrading `anthropic`, rerun tests for: content block access, stop reasons, parallel tool calls, tool-result ordering, error class mapping, retry ownership, custom base URL, and fake-client compatibility.

## Confidence Assessment

| Finding | Confidence | Basis |
|---------|------------|-------|
| Upstream dependency/import map | MEDIUM | Direct inspection of `requirements.txt`, `.env.example`, all 20 canonical `code.py` files, upstream tests, and CI workflow, cross-checked through repository search |
| Keep Python 3.11+ and the existing package shell | MEDIUM | Explicit local constraint plus upstream Python 3.11 CI; all recommended packages support the floor |
| Current package versions | MEDIUM | Current PyPI project pages checked on 2026-07-19; inherently time-sensitive |
| Anthropic tool-loop, retry, timeout, and authentication behavior | MEDIUM | Current official platform documentation and official SDK repository cross-checked; behavior can evolve |
| Minimal pytest strategy | MEDIUM | Official pytest fixtures plus direct upstream test patterns; no third-party plugin is required |
| Defer production MCP SDK | MEDIUM | Direct s19 code inspection identifies its MCP client as a teaching mock; upstream scope explicitly omits full transport/OAuth/runtime details |

## Sources

- [shareAI-lab/learn-claude-code canonical repository](https://github.com/shareAI-lab/learn-claude-code) — chapter sequence, scope, stack, and learning intent.
- [Upstream requirements.txt](https://github.com/shareAI-lab/learn-claude-code/blob/main/requirements.txt) — three runtime dependencies and minimums.
- [Upstream environment template](https://github.com/shareAI-lab/learn-claude-code/blob/main/.env.example) — `ANTHROPIC_API_KEY`, `MODEL_ID`, optional base URL, and provider examples.
- [Upstream s01 implementation](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py) — synchronous client, dotenv, subprocess, and base loop.
- [Upstream s07 implementation](https://github.com/shareAI-lab/learn-claude-code/blob/main/s07_skill_loading/code.py) — first PyYAML use.
- [Upstream s11 implementation](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py) — harness-level retries, jitter, token escalation, and fallback model.
- [Upstream s19 implementation](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py) — mock MCP client and tool-pool assembly without an MCP SDK.
- [Upstream s20 implementation](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py) — complete standard-library and third-party import surface.
- [Upstream Python tests](https://github.com/shareAI-lab/learn-claude-code/tree/main/tests) and [CI workflow](https://github.com/shareAI-lab/learn-claude-code/blob/main/.github/workflows/test.yml) — pytest runner, unittest compatibility, fakes, parametrization, and Python 3.11 CI.
- [Official Anthropic Python SDK documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) — Python requirement, client usage, authentication, retries, errors, and timeouts.
- [Official Anthropic tool-use loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) and [tool-result handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) — manual loop and message-order contract.
- [Anthropic on PyPI](https://pypi.org/project/anthropic/), [pytest on PyPI](https://pypi.org/project/pytest/), [python-dotenv on PyPI](https://pypi.org/project/python-dotenv/), and [PyYAML on PyPI](https://pypi.org/project/PyYAML/) — current releases and Python compatibility.
- [pytest fixture reference](https://docs.pytest.org/en/9.0.x/reference/fixtures.html) and [unittest compatibility](https://docs.pytest.org/en/stable/unittest.html) — built-in test isolation tools and incremental migration support.
- [Python Packaging pyproject metadata specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) — dependency and optional-dependency declarations.

---
*Stack research for: Learn Claude Code by Building*
*Researched: 2026-07-19*
