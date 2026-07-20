# Codebase Structure

**Analysis Date:** 2026-07-21

## Directory Layout

```text
learn-claude-code-by-building/
├── .planning/
│   └── codebase/                  # Generated GSD codebase reference documents
├── learning/                          # Per-chapter narrative and evidence records
│   ├── README.md                  # Required record set for every chapter
│   └── chapter-template.md         # Reusable chapter guide skeleton
├── src/
│   └── mini_claude_code/           # Canonical, continuously evolving Python package
│       ├── __init__.py              # Package marker and runtime version export
│       ├── __main__.py              # `python -m` launcher shim
│       ├── cli.py                   # Shared command-line/application entry point
│       ├── loop.py                  # s01 Agent Loop protocol
│       └── tool.py                  # current teaching bash tool
├── tests/
│   ├── test_smoke.py               # Baseline package and CLI smoke tests
│   └── test_s01_agent_loop.py      # Offline s01 tool loop tests
├── .gitignore                         # Local environment and generated-artifact exclusions
├── AGENTS.md                         # Repository workflow and chapter completion rules
├── README.md                         # Project overview, setup, and baseline commands
└── pyproject.toml                    # Packaging, dependencies, and console-script configuration
```

Generated `__pycache__/` directories may appear beneath `src/mini_claude_code/` and `tests/`; they are ignored runtime artifacts and are not part of the source structure.

## Directory Purposes

**`src/mini_claude_code/`:**
- Purpose: Hold the sole canonical coding-agent harness implementation as it evolves chapter by chapter.
- Contains: Python package metadata, invocation adapters, current Agent Loop modules, and future runtime modules.
- Key files: `src/mini_claude_code/__init__.py`, `src/mini_claude_code/__main__.py`, `src/mini_claude_code/cli.py`, `src/mini_claude_code/loop.py`, `src/mini_claude_code/tool.py`
- Placement rule: Add production behavior here; do not introduce per-chapter source copies elsewhere.

**`tests/`:**
- Purpose: Verify the active package implementation from the consumer-facing import boundary.
- Contains: Python test modules using standard test discovery naming.
- Key files: `tests/test_smoke.py`, `tests/test_s01_agent_loop.py`
- Placement rule: Add tests for new chapter behavior here, named `test_<subject>.py`; retain `tests/test_smoke.py` for baseline package/entry-point coverage.

**`learning/`:**
- Purpose: Preserve chapter goals, deltas, explanations, reflections, runtime evidence, commit hashes, and tags separately from executable code.
- Contains: Repository-wide learning instructions, a chapter template, and future chapter directories.
- Key files: `learning/README.md`, `learning/chapter-template.md`
- Placement rule: For each implemented chapter, create `learning/sXX-short-name/` with `guide.md`, `reflection.md`, and `evidence.md` as required by `learning/README.md`.

**`.planning/codebase/`:**
- Purpose: Store generated, current-state maps used by later GSD planning and execution workflows.
- Contains: Uppercase Markdown reference documents including `.planning/codebase/ARCHITECTURE.md` and `.planning/codebase/STRUCTURE.md`.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`
- Placement rule: Keep planning analysis here; never import it from `src/mini_claude_code/`.

**Repository Root:**
- Purpose: Hold project-wide policy, packaging, setup, and ignore configuration.
- Contains: `AGENTS.md`, `README.md`, `pyproject.toml`, `.gitignore`.
- Key files: `AGENTS.md`, `pyproject.toml`
- Placement rule: Put cross-cutting project metadata at the root; keep executable Python under `src/mini_claude_code/`.

## Key File Locations

**Entry Points:**
- `src/mini_claude_code/cli.py`: Defines the shared `main()` application/CLI callable.
- `src/mini_claude_code/loop.py`: Defines the s01 model/tool loop.
- `src/mini_claude_code/tool.py`: Defines the current bash tool schema and runner.
- `src/mini_claude_code/__main__.py`: Adapts `python -m mini_claude_code` to `main()`.
- `pyproject.toml`: Registers the installed `mini-claude-code` command as `mini_claude_code.cli:main`.
- `tests/test_smoke.py`: Provides a direct test-runner guard in addition to discovery-based execution.

**Configuration:**
- `pyproject.toml`: Defines the Python requirement, build backend, dependencies, development extra, source package discovery, and console script.
- `.gitignore`: Excludes local environments, environment configuration, Python caches, test caches, build outputs, and package metadata.
- `AGENTS.md`: Defines the chapter workflow, definition of done, learning-commit convention, and repository-specific skill restriction.

- **Core Logic:**
- `src/mini_claude_code/cli.py`: Contains CLI environment loading, prompt handling, and final text output.
- `src/mini_claude_code/loop.py`: Contains the current Agent Loop and tool-result correlation behavior.
- `src/mini_claude_code/tool.py`: Contains the current teaching bash tool.
- `src/mini_claude_code/__init__.py`: Exposes the package's current `__version__` value.

**Testing:**
- `tests/test_smoke.py`: Covers importability, the baseline version contract, and direct invocation of `main()`.
- `README.md`: Documents the baseline verification command `python -m unittest discover -s tests -v`.

**Learning Records:**
- `learning/README.md`: Defines the required files and purpose of each chapter record.
- `learning/chapter-template.md`: Provides the initial structure for a chapter guide.
- `README.md`: Defines the 20-chapter evolution model and the single-implementation rule.

## Naming Conventions

**Files:**
- Use lowercase snake_case for Python modules: `src/mini_claude_code/cli.py`, `tests/test_smoke.py`.
- Use Python package protocol names for package entry files: `src/mini_claude_code/__init__.py`, `src/mini_claude_code/__main__.py`.
- Prefix test modules with `test_` so both unittest and pytest can discover them: `tests/test_smoke.py`.
- Use conventional uppercase names for repository-wide documentation and policy: `README.md`, `AGENTS.md`.
- Use lowercase semantic names for chapter artifacts: `guide.md`, `reflection.md`, `evidence.md`, as specified by `learning/README.md`.
- Use uppercase topic names for generated maps: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`.

**Directories:**
- Use lowercase snake_case for importable Python packages: `src/mini_claude_code/`.
- Use plural lowercase names for broad content collections: `tests/`, `learning/`.
- Name each chapter directory `sXX-short-name/`, using a zero-padded sequence and short hyphenated topic slug, as defined in `learning/README.md`.
- Keep generated planning references under the fixed hidden path `.planning/codebase/`.

## Where to Add New Code

**New Harness Feature:**
- Primary code: Add a focused snake_case module under `src/mini_claude_code/` when behavior has a reusable responsibility; keep `src/mini_claude_code/cli.py` as the composition and user-interaction boundary.
- Tests: Add `tests/test_<feature>.py`; import public behavior from `mini_claude_code`, and keep tests independent of chapter Markdown.
- Integration: Wire the new behavior through `src/mini_claude_code/cli.py` so both `src/mini_claude_code/__main__.py` and the console script in `pyproject.toml` receive it.
- Chapter record: Add `learning/sXX-short-name/guide.md`, `learning/sXX-short-name/reflection.md`, and `learning/sXX-short-name/evidence.md` for the same increment.

**New Component/Module:**
- Implementation: `src/mini_claude_code/<component_name>.py`
- Public exposure: Export through `src/mini_claude_code/__init__.py` only when consumers need a package-level API; internal modules can be imported directly by `src/mini_claude_code/cli.py`.
- Invocation rule: Do not put reusable behavior in `src/mini_claude_code/__main__.py`; that file must remain a thin adapter.

**New CLI Behavior:**
- Argument parsing and top-level orchestration: `src/mini_claude_code/cli.py`
- Reusable domain or harness behavior: a dedicated module under `src/mini_claude_code/`, called by `src/mini_claude_code/cli.py`
- Command mapping: Keep `pyproject.toml` targeting `mini_claude_code.cli:main` unless the public command itself is deliberately renamed.
- Tests: `tests/test_cli.py` for focused CLI behavior while `tests/test_smoke.py` retains the baseline entry-point check.

**Utilities:**
- Shared helpers: Add `src/mini_claude_code/<purpose>.py` for helpers with a coherent responsibility; no generic utilities module or utilities directory currently exists.
- Test-only helpers: Keep them under `tests/` once repeated fixture/setup behavior emerges.

**New Test:**
- Unit or component test: `tests/test_<subject>.py`
- Baseline package or launcher assertion: extend `tests/test_smoke.py`
- Follow the existing `unittest.TestCase` discovery structure unless the chapter intentionally establishes another repository-wide test style.

**New Chapter Documentation:**
- Directory: `learning/sXX-short-name/`
- Required files: `learning/sXX-short-name/guide.md`, `learning/sXX-short-name/reflection.md`, `learning/sXX-short-name/evidence.md`
- Starting point: copy the section structure of `learning/chapter-template.md` into the new guide, then replace every placeholder.

## Special Directories

**`src/`:**
- Purpose: Separate installable package source from repository tooling, tests, and documentation.
- Generated: No.
- Committed: Yes.

**`learning/`:**
- Purpose: Store human-readable chapter artifacts that explain and evidence each code increment.
- Generated: No; records are authored as part of chapter completion.
- Committed: Yes.

**`.planning/codebase/`:**
- Purpose: Store generated current-state maps for automated planning and execution workflows.
- Generated: Yes.
- Committed: Intended to be committed; `.gitignore` does not exclude `.planning/`.

**`tests/`:**
- Purpose: Store automated verification separately from production source.
- Generated: No.
- Committed: Yes.

**`__pycache__/`:**
- Purpose: Store Python bytecode caches beneath `src/mini_claude_code/` and `tests/`.
- Generated: Yes.
- Committed: No; excluded by `.gitignore`.

**`.venv/`:**
- Purpose: Hold the repository-local Python virtual environment described in `README.md`.
- Generated: Yes.
- Committed: No; excluded by `.gitignore`.

---

*Structure analysis: 2026-07-21*
