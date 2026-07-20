# Technology Stack

**Analysis Date:** 2026-07-21

## Languages

**Primary:**
- Python 3.11+ - Application package under `src/mini_claude_code/` and smoke tests under `tests/`; the minimum version is declared in `pyproject.toml`.

**Secondary:**
- Markdown - Project instructions and learning records in `README.md`, `AGENTS.md`, and `learning/`.
- TOML - Packaging, dependency, build-system, and console-script configuration in `pyproject.toml`.

## Runtime

**Environment:**
- CPython 3.11 or newer, as required by `pyproject.toml`.
- The active learning environment is the Conda environment `LearnClaudeCode` with Python 3.12.
- The package uses a `src` layout and therefore must be installed before importing `mini_claude_code`, or invoked with `src` on `PYTHONPATH`; see `pyproject.toml` and `src/mini_claude_code/`.

**Package Manager:**
- Conda + uv - Installation instructions use `environment.yml`, `requirements.lock`, and `uv pip install --python "$CONDA_PREFIX/bin/python"`.
- Build backend: `setuptools.build_meta`, with `setuptools>=68`, in `pyproject.toml`.
- Lockfile: `requirements.lock` is present for Python dependencies.

## Frameworks

**Core:**
- No application framework is active. The executable is a plain Python package with `main()` in `src/mini_claude_code/cli.py`.
- Anthropic Python SDK is used by `src/mini_claude_code/loop.py` for the s01 Agent Loop.

**Testing:**
- Python `unittest` standard library - Current test classes and assertions in `tests/test_smoke.py`.
- pytest 8.0+ - Available through the `dev` extra in `pyproject.toml`, but current tests use `unittest` APIs and no pytest configuration is present.

**Build/Dev:**
- setuptools 68+ - Builds and discovers packages under `src/`, configured in `pyproject.toml`.
- pip editable installs - Intended local-development setup in `README.md`.
- `venv` - Intended isolated development environment, documented in `README.md`; `.venv/` is ignored by `.gitignore`.
- No formatter, linter, type checker, task runner, or standalone build configuration is detected.

## Key Dependencies

**Critical:**
- `anthropic>=0.25.0` - Planned provider SDK for the coding-agent model loop; declared in `pyproject.toml` but not yet used by `src/mini_claude_code/`.
- `python-dotenv` - Used by `src/mini_claude_code/cli.py` to load local `.env`.
- `pyyaml>=6.0` - Planned YAML parser; declared in `pyproject.toml` but not yet imported by `src/mini_claude_code/`.

**Infrastructure:**
- No database client, web server, queue, cache, storage SDK, telemetry SDK, or cloud platform dependency is declared in `pyproject.toml`.
- `pytest>=8.0` is the only development-only dependency in `pyproject.toml`.

## Configuration

**Environment:**
- Local model configuration is intended to live in an ignored `.env`, as documented by `README.md` and `.gitignore`.
- `.env.example` exists as the checked-in configuration template; its secret-sensitive contents are intentionally not included in this analysis.
- `.env` loading exists in `src/mini_claude_code/cli.py`; provider API keys must still remain local and uncommitted.
- Never commit `.env`, API keys, or access tokens, per `AGENTS.md` and `.gitignore`.

**Build:**
- `pyproject.toml` is the single build and package manifest.
- `[tool.setuptools.packages.find] where = ["src"]` establishes the package discovery root.
- `[project.scripts]` exposes `mini-claude-code` as `mini_claude_code.cli:main`.
- `src/mini_claude_code/__main__.py` enables `python -m mini_claude_code`.
- No `setup.py`, `setup.cfg`, container definition, or CI build file is detected.

## Platform Requirements

**Development:**
- Install Conda and uv, then create/activate `LearnClaudeCode` following `README.md`.
- Install locked dependencies with `uv pip install --python "$CONDA_PREFIX/bin/python" -r requirements.lock` and the package with `uv pip install --python "$CONDA_PREFIX/bin/python" --no-deps -e .`.
- The documented `python -m unittest discover -s tests -v` command fails in a clean, non-installed checkout because `mini_claude_code` is not on the import path; installation is a prerequisite.
- The baseline CLI has no OS-specific implementation in `src/mini_claude_code/cli.py`.

**Production:**
- No deployment target, container runtime, server process, hosted environment, or production build pipeline is detected.
- The current runtime is a local console program invoked through the installed `mini-claude-code` script or `python -m mini_claude_code`.
- Preserve the evolving single-package implementation in `src/mini_claude_code/`, as required by `AGENTS.md`.

---

*Stack analysis: 2026-07-21*
