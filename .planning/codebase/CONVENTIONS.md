# Coding Conventions

**Analysis Date:** 2026-07-19

## Naming Patterns

**Files:**
- Use lowercase `snake_case.py` for Python modules. The current implementation uses `src/mini_claude_code/cli.py`, and tests use the `test_*.py` discovery form in `tests/test_smoke.py`.
- Reserve `src/mini_claude_code/__init__.py` for package metadata and public package exports, and `src/mini_claude_code/__main__.py` for `python -m mini_claude_code` dispatch.
- Name chapter directories `learning/sXX-short-name/` and keep `guide.md`, `reflection.md`, and `evidence.md` inside each chapter, as specified by `learning/README.md`.

**Functions:**
- Use lowercase `snake_case` for functions and test methods: `main()` in `src/mini_claude_code/cli.py`, `test_package_has_baseline_version()`, and `test_cli_entry_point_runs()` in `tests/test_smoke.py`.
- Add explicit return annotations to implementation and test functions. Existing functions use `-> None` in `src/mini_claude_code/cli.py` and `tests/test_smoke.py`.
- Prefix test methods with `test_` so both `unittest` discovery and pytest compatibility work, following `tests/test_smoke.py`.

**Variables:**
- Use lowercase `snake_case` for ordinary variables when introduced. No ordinary local or module variables exist yet beyond package metadata in `src/mini_claude_code/__init__.py`.
- Use double-underscore module metadata names where Python defines the convention; the package version is `__version__` in `src/mini_claude_code/__init__.py`.

**Types:**
- Use `PascalCase` for classes. Test cases follow this rule with `BaselineSmokeTest` in `tests/test_smoke.py`.
- Use descriptive role/scope suffixes for test classes, such as `SmokeTest`, rather than generic names; `BaselineSmokeTest` in `tests/test_smoke.py` establishes the current pattern.
- No application-defined type aliases, dataclasses, protocols, or enums are present. Place new harness types under `src/mini_claude_code/` and name them in `PascalCase`.

## Code Style

**Formatting:**
- No formatter configuration is present in the repository; `pyproject.toml` contains only build, project, script, dependency, and setuptools package-discovery settings.
- Follow the compact PEP 8-compatible formatting visible in `src/mini_claude_code/cli.py` and `tests/test_smoke.py`: four-space indentation, two blank lines before top-level definitions, spaces around operators, and a trailing newline.
- Use double quotes for Python string literals and docstrings, matching `src/mini_claude_code/__init__.py` and `src/mini_claude_code/cli.py`.
- Keep one evolving implementation under `src/mini_claude_code/` instead of copying per-chapter implementations, as required by `AGENTS.md`.

**Linting:**
- No linter or static type checker is configured. There is no Ruff, Flake8, Pylint, mypy, or Pyright configuration in `pyproject.toml` or at repository root.
- Preserve explicit type annotations on all newly added functions even though no type-checking command is currently enforced; this matches `src/mini_claude_code/cli.py` and `tests/test_smoke.py`.
- Do not add secrets, API keys, access tokens, or `.env` to source control; this is an explicit repository rule in `AGENTS.md`, and `.env` is ignored by `.gitignore`.
- Do not use skills whose names begin with `trn-` for this agent-learning repository; the restriction is defined in `AGENTS.md`.

## Import Organization

**Order:**
1. Standard-library imports, as shown by `import unittest` at the top of `tests/test_smoke.py`.
2. A blank line separating import groups, as in `tests/test_smoke.py`.
3. Absolute package imports from `mini_claude_code`, as used by `tests/test_smoke.py` and `src/mini_claude_code/__main__.py`.

**Path Aliases:**
- No path aliases are configured. Import application code through the installed `mini_claude_code` package, not through `src`-prefixed imports; see `from mini_claude_code.cli import main` in `src/mini_claude_code/__main__.py`.
- The `src/` layout is configured by `[tool.setuptools.packages.find] where = ["src"]` in `pyproject.toml`; local commands therefore require an editable install or `PYTHONPATH=src`.
- Prefer absolute intra-package imports, following `src/mini_claude_code/__main__.py`, until the codebase establishes a different local convention.

## Error Handling

**Patterns:**
- No application error-handling abstraction exists yet. `main()` in `src/mini_claude_code/cli.py` performs a deterministic print and allows exceptions to propagate.
- Keep the CLI entry point in `src/mini_claude_code/__main__.py` thin: delegate to `mini_claude_code.cli.main()` and use the `if __name__ == "__main__":` guard.
- Introduce error handling beside the mechanism that owns the failure rather than swallowing exceptions in `src/mini_claude_code/__main__.py`; tests should cover the externally visible behavior in `tests/`.
- Do not catch broad exceptions without a specific recovery or user-facing conversion. No broad `except` blocks are present in `src/mini_claude_code/`.

## Logging

**Framework:** `print` only

**Patterns:**
- The sole runtime message is printed directly by `main()` in `src/mini_claude_code/cli.py`.
- No `logging` setup, structured logger, verbosity flag, or log-level configuration is present.
- Keep user-facing CLI output in `src/mini_claude_code/cli.py`; do not emit output from package initialization in `src/mini_claude_code/__init__.py`.
- Tests may invoke the CLI directly, as `tests/test_smoke.py` does, but output-sensitive behavior should be captured and asserted when message content becomes part of the contract.

## Comments

**When to Comment:**
- Prefer a concise module docstring that states responsibility. `src/mini_claude_code/cli.py` documents the command-line role, and `src/mini_claude_code/__init__.py` describes the package as incrementally built.
- Use chapter documentation, not long source comments, for conceptual explanations. Put goals, data flow, reading order, tasks, acceptance criteria, and questions in chapter material based on `learning/chapter-template.md`.
- No `TODO`, `FIXME`, `HACK`, or `XXX` comments are present. Track incomplete learning work with checklist items in `learning/chapter-template.md` rather than hidden code comments.

**JSDoc/TSDoc:**
- Not applicable; the repository is Python.
- Python function docstrings are not yet used because `main()` is self-contained. Add docstrings to public or non-obvious functions as the harness grows, while keeping module-level purpose docstrings consistent with `src/mini_claude_code/cli.py`.

## Function Design

**Size:** Keep functions focused on one harness responsibility. The only function, `main()` in `src/mini_claude_code/cli.py`, is three lines including its signature and output statement.

**Parameters:** Use annotated parameters when inputs are introduced. The current CLI entry point accepts no parameters and is annotated `main() -> None` in `src/mini_claude_code/cli.py`.

**Return Values:** Use explicit return annotations and allow command functions that exist for side effects to return `None`, matching `src/mini_claude_code/cli.py`. Tests should assert returned values when a function has a value contract rather than testing only that it executes.

## Module Design

**Exports:**
- Keep package metadata in `src/mini_claude_code/__init__.py`; it currently exports `__version__` implicitly.
- Keep command implementation in `src/mini_claude_code/cli.py`, and make both the console script in `pyproject.toml` and module launcher in `src/mini_claude_code/__main__.py` delegate to the same `main()` function.
- Add each chapter's mechanism to the evolving package under `src/mini_claude_code/`, preserving a single implementation as required by `AGENTS.md`.

**Barrel Files:**
- No barrel/re-export module is used. `src/mini_claude_code/__init__.py` contains only package metadata, while consumers import `main` from `mini_claude_code.cli` in `tests/test_smoke.py`.
- Avoid adding broad re-exports until a stable public API exists; import from the owning module as `tests/test_smoke.py` does.

---

*Convention analysis: 2026-07-19*
