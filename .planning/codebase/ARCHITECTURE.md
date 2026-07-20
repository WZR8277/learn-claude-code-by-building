<!-- refreshed: 2026-07-21 -->
# Architecture

**Analysis Date:** 2026-07-21

## System Overview

```text
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│ Console script     │  │ Module execution   │  │ Direct Python call │
│ `pyproject.toml`   │  │ `__main__.py`      │  │ tests/importers    │
└──────────┬─────────┘  └──────────┬─────────┘  └──────────┬─────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────┐
│                       CLI boundary                           │
│              `src/mini_claude_code/cli.py`                  │
└──────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────┐
│                 Agent Loop and tool boundary                 │
│   model call -> tool_use -> local bash -> tool_result -> stop │
└──────────────────────────────────────────────────────────┘
```

The repository has completed `s01-agent-loop`. It now contains a minimal synchronous model/tool feedback loop, a single bash tool, `.env` loading at the CLI boundary, and offline fake-client tests for `tool_use`/`tool_result` correlation. The next phase is `s02 Tool Use`, which should expand tool registration and guarded dispatch without prebuilding permissions or hooks.

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Package metadata | Identifies the evolving harness package and exposes its current version | `src/mini_claude_code/__init__.py` |
| Module launcher | Supports `python -m mini_claude_code` and delegates immediately to the CLI | `src/mini_claude_code/__main__.py` |
| CLI boundary | Owns `.env` loading, terminal input/output, readline setup, and the single public `main()` callable | `src/mini_claude_code/cli.py` |
| Agent loop | Calls the model, appends assistant content, executes requested tools, and appends correlated `tool_result` blocks | `src/mini_claude_code/loop.py` |
| Tool boundary | Defines the teaching `bash` tool and bounded subprocess execution helper | `src/mini_claude_code/tool.py` |
| Installed command mapping | Maps the `mini-claude-code` console command to the same `main()` callable | `pyproject.toml` |
| Baseline verification | Exercises package import, version exposure, callable CLI entry, and s01 loop behavior | `tests/test_smoke.py`, `tests/test_s01_agent_loop.py` |
| Learning records | Defines the per-chapter documentation contract that accompanies code evolution | `learning/README.md` |

## Pattern Overview

**Overall:** Minimal layered command-line package with a single shared application entry point

**Key Characteristics:**
- Both supported shell entry paths converge on `mini_claude_code.cli:main`, keeping invocation-specific code outside the evolving implementation.
- The package uses a `src/` layout, so application imports resolve from `src/mini_claude_code/` after installation or an equivalent test-path setup.
- Runtime behavior is synchronous and conversation-history based: CLI input appends user messages, the agent loop appends assistant content and tool results, and control returns when the model does not request a tool.
- Production code evolves in place under `src/mini_claude_code/`; chapter history belongs in adjacent records under `learning/sXX-*/` rather than copied source snapshots.

## Layers

**Packaging and Invocation Layer:**
- Purpose: Turn an installed command or module execution into a Python function call.
- Location: `pyproject.toml`, `src/mini_claude_code/__main__.py`
- Contains: A setuptools console-script declaration and the `if __name__ == "__main__"` module guard.
- Depends on: `src/mini_claude_code/cli.py`.
- Used by: Shell users invoking `mini-claude-code` or `python -m mini_claude_code`.

**CLI/Application Boundary:**
- Purpose: Provide the stable public callable into which each chapter's harness behavior can be integrated.
- Location: `src/mini_claude_code/cli.py`
- Contains: `main()`, `.env` loading, interactive prompt handling, and final text block printing.
- Depends on: `python-dotenv`, `src/mini_claude_code/loop.py`, and standard terminal I/O.
- Used by: `src/mini_claude_code/__main__.py`, the console script in `pyproject.toml`, and `tests/test_smoke.py`.

**Agent Loop Layer:**
- Purpose: Maintain the minimal model/tool loop introduced in s01.
- Location: `src/mini_claude_code/loop.py`
- Contains: `agent_loop(messages, client=None, tool_runner=run_bash)`, the system prompt, model call, stop condition, and tool-result construction.
- Depends on: Anthropic-compatible client interface and `src/mini_claude_code/tool.py`.
- Used by: `src/mini_claude_code/cli.py` and `tests/test_s01_agent_loop.py`.

**Tool Layer:**
- Purpose: Provide the current teaching tool surface for local command execution.
- Location: `src/mini_claude_code/tool.py`
- Contains: `TOOLS` and `run_bash(command)`.
- Depends on: `subprocess` and `os`.
- Used by: `src/mini_claude_code/loop.py`.

**Package Metadata Layer:**
- Purpose: Mark the directory as an importable package and expose the runtime version.
- Location: `src/mini_claude_code/__init__.py`
- Contains: The `__version__` package attribute.
- Depends on: Nothing.
- Used by: `tests/test_smoke.py` and package consumers that inspect the version.

**Verification Layer:**
- Purpose: Assert the bootstrap package contract without depending on future model or tool integrations.
- Location: `tests/test_smoke.py`
- Contains: `unittest.TestCase` smoke tests and a direct test-module runner guard.
- Depends on: `src/mini_claude_code/__init__.py`, `src/mini_claude_code/cli.py`, and Python `unittest`.
- Used by: `python -m unittest discover -s tests -v`; it is also discoverable by the declared pytest development dependency.

**Learning-Evidence Layer:**
- Purpose: Record the problem, chapter delta, implementation evidence, and reflection alongside the evolving codebase.
- Location: `learning/README.md`, `learning/chapter-template.md`, future `learning/sXX-*/` directories.
- Contains: Markdown conventions and the reusable chapter guide template.
- Depends on: The chapter workflow in `AGENTS.md` and `README.md`.
- Used by: Each chapter's learning and commit process; it is not imported by runtime code.

## Data Flow

### Primary Request Path

1. `python -m mini_claude_code` loads the package module launcher and imports `main`.
2. The module guard invokes the shared callable.
3. `main()` loads `.env`, starts the interactive prompt, appends user messages to `history`, and calls `agent_loop(history)`.
4. `agent_loop()` calls the model. If the response requests tools, it executes each `tool_use` through the current tool runner and appends matching `tool_result` blocks. If the response does not request tools, it returns to the CLI.

### Installed Console-Script Path

1. Package installation registers `mini-claude-code` against `mini_claude_code.cli:main` (`pyproject.toml:20`).
2. The generated launcher imports and calls `main()` directly; `src/mini_claude_code/__main__.py` is bypassed.
3. `main()` runs the same CLI and Agent Loop path as module execution.

### Baseline Test Flow

1. Test discovery imports the package version and CLI callable (`tests/test_smoke.py:3`).
2. One test compares the exported version to the expected bootstrap value (`tests/test_smoke.py:8`).
3. One test directly calls `main()`, exercising the CLI boundary without spawning a subprocess (`tests/test_smoke.py:11`).

**State Management:**
- Conversation state is an in-memory `history` list owned by the CLI for the current process.
- Model configuration is loaded from ignored `.env` into environment variables.
- No persistent runtime state, cache, task store, permission database, or memory system exists yet.

## Key Abstractions

**Shared CLI Callable:**
- Purpose: Give console scripts, module execution, tests, and Python importers one stable entry point.
- Examples: `src/mini_claude_code/cli.py`, `src/mini_claude_code/__main__.py`, `pyproject.toml`
- Pattern: Thin adapter / command boundary.

**Evolving Harness Package:**
- Purpose: Hold the one continuously developed coding-agent implementation across all chapters.
- Examples: `src/mini_claude_code/__init__.py`, `src/mini_claude_code/cli.py`
- Pattern: `src`-layout Python package, intentionally not versioned as per-chapter source copies.

**Chapter Record:**
- Purpose: Bind a chapter's goal and delta to its reflection, runtime evidence, commit, and tag.
- Examples: `learning/README.md`, `learning/chapter-template.md`
- Pattern: Documentation-as-evidence with future `learning/sXX-short-name/` directories.

## Entry Points

**Module Entry Point:**
- Location: `src/mini_claude_code/__main__.py`
- Triggers: `python -m mini_claude_code`
- Responsibilities: Import and invoke the CLI `main()` function only when executed as the package module.

**Installed Console Entry Point:**
- Location: `pyproject.toml`
- Triggers: `mini-claude-code` after package installation.
- Responsibilities: Resolve the command to `mini_claude_code.cli:main`.

**Direct Python Entry Point:**
- Location: `src/mini_claude_code/cli.py`
- Triggers: Importers and tests calling `main()`.
- Responsibilities: Own top-level CLI orchestration and return normally after output.

**Test Entry Point:**
- Location: `tests/test_smoke.py`
- Triggers: `python -m unittest discover -s tests -v`, direct module execution, or pytest collection.
- Responsibilities: Verify the package bootstrap contract.

## Architectural Constraints

- **Threading:** Execution is single-threaded and synchronous. `run_bash` uses bounded subprocess execution; no async functions, worker threads, or task scheduler exist yet.
- **Global state:** Avoid creating provider clients or mutable conversation state at import time. s01 keeps client creation inside `agent_loop()` for testability and `.env` ordering.
- **Circular imports:** Keep launchers thin. Dependency direction is `__main__.py -> cli.py -> loop.py -> tool.py`.
- **Stable command target:** Keep `mini_claude_code.cli:main` valid because `pyproject.toml`, `src/mini_claude_code/__main__.py`, and `tests/test_smoke.py` all depend on it.
- **Chapter evolution:** Modify the single package under `src/mini_claude_code/` and add corresponding records under `learning/sXX-short-name/`; do not create parallel implementation snapshots. This contract is explicit in `AGENTS.md` and `README.md`.
- **Current stage:** s01 has introduced model access, environment loading, one bash tool, and the Agent Loop. s02 should expand tool dispatch and registry behavior only.

## Anti-Patterns

### Putting Runtime Logic in Launchers

**What happens:** Invocation-specific files such as `src/mini_claude_code/__main__.py` accumulate agent-loop, model, or tool behavior.
**Why it's wrong:** The installed console script bypasses `__main__.py`, so behavior would differ between the two documented commands.
**Do this instead:** Keep `src/mini_claude_code/__main__.py` as a delegation shim and compose runtime behavior behind `main()` in `src/mini_claude_code/cli.py` or modules imported by it.

### Copying the Implementation Per Chapter

**What happens:** New source trees are created for `s01`, `s02`, and later chapters.
**Why it's wrong:** It breaks the repository's explicit evolving-codebase model, makes the canonical runtime ambiguous, and separates tests from the active implementation.
**Do this instead:** Evolve `src/mini_claude_code/` in place and preserve chapter-specific narrative and evidence in `learning/sXX-short-name/` as specified by `learning/README.md`.

### Treating Declared Dependencies as Implemented Layers

**What happens:** Callers assume Anthropic model access, dotenv loading, or YAML configuration already exists because the packages appear in `pyproject.toml`.
**Why it's wrong:** No file under `src/mini_claude_code/` imports or configures these packages at the `s00` stage.
**Do this instead:** Base integrations and internal boundaries on implemented modules and tests, beginning from `src/mini_claude_code/cli.py`; add each layer only with its chapter's code, tests, and evidence.

## Error Handling

**Strategy:** s01 uses teaching-level error handling: CLI exit on EOF/interrupt, bounded bash timeout, and tool failures returned as text content. Later chapters will make errors more structured.

**Patterns:**
- `src/mini_claude_code/cli.py` catches `EOFError`, `KeyboardInterrupt`, and pytest stdin `OSError` to end the prompt loop.
- `src/mini_claude_code/__main__.py` does not translate return values into exit codes; `main()` currently returns `None`.
- Add exception translation at the CLI boundary only when a chapter defines recoverable domain errors; keep reusable internal functions independent of process exits.

## Cross-Cutting Concerns

**Logging:** Not detected. `src/mini_claude_code/cli.py` uses `print()` for user-facing baseline output, not structured diagnostics.
**Validation:** Minimal validation exists for blocked dangerous bash substrings. s02 should replace this with clearer tool registration and guarded dispatch behavior.
**Authentication:** The Anthropic-compatible SDK reads `ANTHROPIC_API_KEY` from environment after `.env` loading. Secrets remain outside Git and Feishu.

---

*Architecture analysis: 2026-07-21*
