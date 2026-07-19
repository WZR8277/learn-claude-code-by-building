<!-- refreshed: 2026-07-19 -->
# Architecture

**Analysis Date:** 2026-07-19

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
│                     Standard output                          │
│          Baseline status text; no agent runtime yet          │
└──────────────────────────────────────────────────────────┘
```

The repository is at the `s00` bootstrap stage documented in `README.md`; it provides a package and invocation shell but does not yet contain the agent loop, model client, tools, session state, or configuration loading implied by its declared dependencies in `pyproject.toml`.

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Package metadata | Identifies the evolving harness package and exposes its current version | `src/mini_claude_code/__init__.py` |
| Module launcher | Supports `python -m mini_claude_code` and delegates immediately to the CLI | `src/mini_claude_code/__main__.py` |
| CLI boundary | Owns the single public `main()` callable and current stdout response | `src/mini_claude_code/cli.py` |
| Installed command mapping | Maps the `mini-claude-code` console command to the same `main()` callable | `pyproject.toml` |
| Baseline verification | Exercises package import, version exposure, and callable CLI entry | `tests/test_smoke.py` |
| Learning records | Defines the per-chapter documentation contract that accompanies code evolution | `learning/README.md` |

## Pattern Overview

**Overall:** Minimal layered command-line package with a single shared application entry point

**Key Characteristics:**
- Both supported shell entry paths converge on `mini_claude_code.cli:main`, keeping invocation-specific code outside the evolving implementation.
- The package uses a `src/` layout, so application imports resolve from `src/mini_claude_code/` after installation or an equivalent test-path setup.
- Runtime behavior is currently stateless and synchronous: one function writes one line to standard output and returns `None`.
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
- Contains: `main()`, currently a baseline status print only.
- Depends on: Python's built-in `print`; no internal service layer exists yet.
- Used by: `src/mini_claude_code/__main__.py`, the console script in `pyproject.toml`, and `tests/test_smoke.py`.

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

1. `python -m mini_claude_code` loads the package module launcher and imports `main` (`src/mini_claude_code/__main__.py:1`).
2. The module guard invokes the shared callable (`src/mini_claude_code/__main__.py:4`).
3. `main()` emits the `s00` readiness message to standard output and returns implicitly (`src/mini_claude_code/cli.py:4`).

### Installed Console-Script Path

1. Package installation registers `mini-claude-code` against `mini_claude_code.cli:main` (`pyproject.toml:20`).
2. The generated launcher imports and calls `main()` directly; `src/mini_claude_code/__main__.py` is bypassed.
3. `main()` writes the same readiness message to standard output (`src/mini_claude_code/cli.py:5`).

### Baseline Test Flow

1. Test discovery imports the package version and CLI callable (`tests/test_smoke.py:3`).
2. One test compares the exported version to the expected bootstrap value (`tests/test_smoke.py:8`).
3. One test directly calls `main()`, exercising the CLI boundary without spawning a subprocess (`tests/test_smoke.py:11`).

**State Management:**
- No runtime state store, conversation history, configuration object, cache, or module-level mutable singleton is present. The only package-level datum is immutable version text in `src/mini_claude_code/__init__.py`.

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

- **Threading:** Execution is single-threaded and synchronous; no async functions, worker threads, subprocesses, or task scheduler exist in `src/mini_claude_code/`.
- **Global state:** `src/mini_claude_code/__init__.py` exposes only the immutable `__version__` string. Do not introduce shared mutable conversation or tool state at import time.
- **Circular imports:** None detected. Dependency direction is one-way from `src/mini_claude_code/__main__.py` to `src/mini_claude_code/cli.py`; `cli.py` imports no application module.
- **Stable command target:** Keep `mini_claude_code.cli:main` valid because `pyproject.toml`, `src/mini_claude_code/__main__.py`, and `tests/test_smoke.py` all depend on it.
- **Chapter evolution:** Modify the single package under `src/mini_claude_code/` and add corresponding records under `learning/sXX-short-name/`; do not create parallel implementation snapshots. This contract is explicit in `AGENTS.md` and `README.md`.
- **Current stage:** Treat model access, environment loading, YAML configuration, tool dispatch, and agent-loop boundaries as absent until their chapter introduces them; their packages being declared in `pyproject.toml` does not establish architecture by itself.

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

**Strategy:** No explicit error-handling strategy exists because the current runtime performs no fallible I/O beyond a direct stdout write.

**Patterns:**
- `src/mini_claude_code/cli.py` does not catch exceptions; future unexpected failures therefore propagate to the launcher and produce a non-zero process failure naturally.
- `src/mini_claude_code/__main__.py` does not translate return values into exit codes; `main()` currently returns `None`.
- Add exception translation at the CLI boundary only when a chapter defines recoverable domain errors; keep reusable internal functions independent of process exits.

## Cross-Cutting Concerns

**Logging:** Not detected. `src/mini_claude_code/cli.py` uses `print()` for user-facing baseline output, not structured diagnostics.
**Validation:** Not applicable at `s00`; there are no arguments, configuration values, prompts, or external responses to validate.
**Authentication:** Not implemented. `README.md` references local environment configuration, but runtime code in `src/mini_claude_code/` does not load or consume credentials.

---

*Architecture analysis: 2026-07-19*
