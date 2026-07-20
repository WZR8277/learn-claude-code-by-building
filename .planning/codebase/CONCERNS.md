# Codebase Concerns

**Analysis Date:** 2026-07-19

## Tech Debt

**Unreproducible dependency resolution:**
- Issue: All runtime and development dependencies are open-ended lower bounds, and the repository has no lockfile or constraints file. A fresh installation can resolve a different dependency graph over time.
- Files: `pyproject.toml`
- Impact: Chapter evidence is not reliably reproducible; a future release of `anthropic`, `python-dotenv`, `pyyaml`, `pytest`, or a transitive package can change behavior or break installation without a source change.
- Fix approach: Add a committed lock or constraints file generated for the supported Python versions, keep broad declarations in `pyproject.toml` if desired, and make chapter evidence record the resolved environment.

**Premature runtime dependency surface:**
- Issue: `anthropic`, `python-dotenv`, and `pyyaml` are installed even though the current implementation imports none of them; the executable only prints a status line.
- Files: `pyproject.toml`, `src/mini_claude_code/cli.py`
- Impact: The baseline has unnecessary installation time, resolver variability, and supply-chain exposure before the corresponding capabilities exist.
- Fix approach: Introduce each dependency in the chapter that first uses it, or document that the dependency list intentionally reserves the full-course stack and pin its resolved versions.

**Version declared in two places:**
- Issue: Version `0.0.0` is duplicated in package metadata and Python source.
- Files: `pyproject.toml`, `src/mini_claude_code/__init__.py`
- Impact: Releases can expose inconsistent versions depending on whether callers inspect installed metadata or `mini_claude_code.__version__`.
- Fix approach: Keep one source of truth; read the installed version with `importlib.metadata.version()` or configure the build backend to derive metadata from `src/mini_claude_code/__init__.py`.

**No automated quality gates:**
- Issue: The repository defines pytest as a development dependency but has no CI workflow, coverage configuration, formatter, linter, type checker, or pre-commit configuration.
- Files: `pyproject.toml`, `tests/test_smoke.py`, `AGENTS.md`
- Impact: The chapter completion rules depend on manual discipline, so commits and tags can be created with failing tests, style drift, or type errors.
- Fix approach: Add a minimal CI job that installs the locked development environment and runs tests; add linting, formatting, and type checking only when their configuration is committed and documented.

**Chapter protocol is not mechanically verified:**
- Issue: Chapter records, one-commit-per-chapter history, matching `sXX-*` tags, evidence completion, and Feishu synchronization are requirements expressed mostly in prose. s01 now has a commit/tag/Feishu record, but later chapters still depend on disciplined checks.
- Files: `AGENTS.md`, `README.md`, `learning/README.md`, `learning/chapter-template.md`
- Impact: The learning history can silently diverge from the defining workflow, reducing the value of the repository as a chapter-by-chapter reconstruction.
- Fix approach: Add a read-only validation script and CI check for directory naming, required record files, completed checklist fields, tag naming, and commit/tag correspondence. Treat external Feishu state as an explicitly recorded evidence item rather than assuming it can be inferred from Git.

## Known Bugs

**No demonstrated runtime defect in the implemented baseline:**
- Symptoms: The current CLI prints its `s00` message, and the two smoke tests pass under Python with `src` on the import path.
- Files: `src/mini_claude_code/cli.py`, `src/mini_claude_code/__main__.py`, `tests/test_smoke.py`
- Trigger: Not applicable to the implemented `s00` behavior; no agent loop, model call, configuration loader, or tool execution path exists yet.
- Workaround: Not applicable. Preserve the passing baseline while adding assertions that verify behavior rather than merely exercise code.

## Security Considerations

**Environment-file ignore pattern is too narrow:**
- Risk: `.gitignore` excludes `.env` but does not exclude common secret-bearing variants such as `.env.local`, `.env.development`, or `.env.production`. The repository intentionally tracks `.env.example`, so a blanket `.env.*` rule requires an explicit exception for that safe template.
- Files: `.gitignore`, `.env.example`, `README.md`, `AGENTS.md`
- Current mitigation: `AGENTS.md` prohibits committing secrets, API keys, access tokens, and `.env`; `README.md` directs users to copy the tracked example into the ignored `.env` file.
- Recommendations: Ignore `.env.*`, re-include `.env.example`, add secret scanning in CI, and keep only placeholder names—not usable values—in the example file.

**Agent safety controls do not yet exist:**
- Risk: The project is intended to become a coding-agent harness, but the current package has no workspace boundary, command allow/deny policy, destructive-action confirmation, timeout, output limit, secret redaction, or audit trail.
- Files: `README.md`, `learning/chapter-template.md`, `src/mini_claude_code/cli.py`
- Current mitigation: No command execution, file mutation, model invocation, or external input is implemented, so the current `s00` executable has no active tool-execution attack surface. The chapter template requires a “safe runtime demonstration” but does not define enforceable safety properties.
- Recommendations: Before adding tools, define a workspace-root capability model; validate resolved paths; avoid implicit shells; bound time and output; require confirmation for destructive actions; redact environment values; and add adversarial tests for traversal, injection, symlinks, and prompt-supplied commands.

**Third-party model and configuration libraries are unconstrained:**
- Risk: Installing latest-compatible versions from open-ended ranges increases exposure to unreviewed upstream behavior and transitive dependency changes.
- Files: `pyproject.toml`
- Current mitigation: Python 3.11 or newer is required, and no third-party dependency is imported by the current runtime.
- Recommendations: Lock resolved versions, enable dependency vulnerability and license scanning, and review upgrades deliberately alongside chapter evidence.

**External-model data policy is unspecified:**
- Risk: The declared Anthropic client indicates future outbound model traffic, but the repository has no documented rules for excluding secrets, local source, personal data, or command output from prompts and logs.
- Files: `pyproject.toml`, `README.md`, `AGENTS.md`
- Current mitigation: `AGENTS.md` prohibits committing secrets, while the current implementation makes no model calls.
- Recommendations: Define prompt-data classification and redaction before the first API call; default to explicit file selection, avoid sending environment contents, and test that secrets cannot enter requests or recorded evidence.

## Performance Bottlenecks

**No active runtime bottleneck detected:**
- Problem: The implemented program performs one constant-time `print` and has no loop, I/O, subprocess, parser, or network request to profile.
- Files: `src/mini_claude_code/cli.py`, `src/mini_claude_code/__main__.py`
- Cause: Not applicable at the `s00` scaffold.
- Improvement path: Do not optimize the placeholder. Add elapsed-time and token/tool-call measurements when the agent loop and model integration are introduced, then profile evidence-backed hotspots.

**Fresh-environment setup does unnecessary work:**
- Problem: Editable installation resolves and installs three runtime libraries before any of them is used by the executable.
- Files: `pyproject.toml`, `README.md`, `src/mini_claude_code/cli.py`
- Cause: The dependency declaration anticipates future chapters rather than matching the current implementation.
- Improvement path: Stage dependencies by chapter or use locked optional extras so the baseline installs only what it executes.

## Fragile Areas

**CLI behavior has no behavioral assertion:**
- Files: `src/mini_claude_code/cli.py`, `src/mini_claude_code/__main__.py`, `tests/test_smoke.py`
- Why fragile: `test_cli_entry_point_runs` calls `main()` but never asserts stdout, exit behavior, or the module entry point. It passes if the message is wrong or removed, as long as no exception is raised.
- Safe modification: Capture stdout and assert the intended message and newline; invoke `python -m mini_claude_code` or an equivalent isolated entry-point test for packaging behavior.
- Test coverage: There is no test for `src/mini_claude_code/__main__.py`, the installed `mini-claude-code` script, stderr, or exit codes.

**Source-layout imports depend on environment setup:**
- Files: `pyproject.toml`, `README.md`, `tests/test_smoke.py`
- Why fragile: Tests import `mini_claude_code` directly from a `src/` layout, so they rely on the editable-install step or an externally supplied `PYTHONPATH`; the test command itself does not prove that packaging/install metadata is valid.
- Safe modification: Run tests against a built and installed wheel in CI in addition to fast editable-source tests.
- Test coverage: No build, wheel-install, console-script, or clean-environment test is present.

**Single evolving implementation concentrates regression risk:**
- Files: `AGENTS.md`, `README.md`, `src/mini_claude_code/`, `tests/test_smoke.py`
- Why fragile: Every chapter modifies the same package, while prior chapter behavior is preserved only by whatever tests remain. There are currently only two baseline tests.
- Safe modification: Keep cumulative regression tests for each mechanism and record explicit compatibility expectations in each `learning/sXX-*/guide.md` rather than replacing earlier tests as chapters advance.
- Test coverage: No historical contract suite or chapter-specific test organization exists yet.

**Learning evidence is free-form:**
- Files: `learning/chapter-template.md`, `learning/README.md`, `AGENTS.md`
- Why fragile: Placeholder prose and checklist boxes can be left incomplete, and evidence fields have no machine-readable schema.
- Safe modification: Define required headings and verifiable fields for commands, results, commit hash, and tag; validate them without trying to automate the learner’s reflection content.
- Test coverage: No repository test checks chapter record completeness or cross-references.

## Scaling Limits

**Harness execution capacity is one placeholder invocation:**
- Current capacity: One synchronous CLI call that prints a fixed message; there is no session, task queue, concurrency, persistence, or retry mechanism.
- Limit: The package cannot execute even one agent turn, so throughput and multi-user scaling are not yet meaningful.
- Scaling path: First implement and test one bounded sequential agent loop in `src/mini_claude_code/`; add concurrency only after tool isolation, cancellation, rate limiting, and deterministic per-session state exist.

**Repository workflow scales manually with chapter count:**
- Current capacity: Chapter artifacts are manually created from one template and validated by human review.
- Limit: As `learning/` approaches the documented 20 chapters, missing files, mismatched tags, and stale evidence become increasingly difficult to detect by inspection.
- Scaling path: Add a validator for `learning/sXX-*/` and Git metadata, and run it in CI while preserving reflection as human-authored content.

## Dependencies at Risk

**`anthropic>=0.25.0`:**
- Files: `pyproject.toml`
- Risk: The lower bound permits a wide range of SDK interfaces, including future major releases, without a lockfile proving which API the code targets.
- Impact: Model-client code added in later chapters can break on clean install or behave differently from recorded evidence.
- Migration plan: Select and lock a tested SDK version when the model-integration chapter begins; isolate SDK calls behind a small adapter so upgrades do not spread through the agent loop.

**`setuptools>=68`:**
- Files: `pyproject.toml`
- Risk: The build environment may fetch a different backend version on each isolated build.
- Impact: Wheel metadata and package discovery can change independently of repository code.
- Migration plan: Constrain build requirements through the chosen reproducible build workflow and verify wheel contents in CI.

**`python-dotenv>=1.0.0` and `pyyaml>=6.0`:**
- Files: `pyproject.toml`
- Risk: They expand configuration parsing and supply-chain surface before configuration behavior or schema is defined.
- Impact: Future code may accept unvalidated strings or YAML structures as trusted agent configuration.
- Migration plan: Add typed validation at the boundary, use safe YAML loading only, reject unknown or dangerous configuration, and lock tested versions when introduced.

## Missing Critical Features

**Core agent loop:**
- Problem: Historical note: before s01, the repository explicitly remained at `s00`; `main()` only printed that the Agent Loop comes in `s01`. s01 has since replaced this with the first Agent Loop implementation.
- Blocks: Model interaction, turn state, stopping conditions, tool calling, error recovery, and every end-to-end coding-agent workflow.
- Files: `README.md`, `src/mini_claude_code/cli.py`

**Configuration contract:**
- Problem: An environment example and dotenv dependency exist, but there is no configuration loader, schema, validation, startup diagnostic, or documented variable contract in executable code.
- Blocks: Predictable model selection, authenticated API calls, safe defaults, and actionable configuration errors.
- Files: `.env.example`, `pyproject.toml`, `README.md`, `src/mini_claude_code/cli.py`

**Tool security boundary:**
- Problem: No file or command tool contract defines allowed roots, input validation, authorization, cancellation, or audit output.
- Blocks: Safely implementing the coding capabilities implied by the project goal.
- Files: `README.md`, `learning/chapter-template.md`, `src/mini_claude_code/cli.py`

## Test Coverage Gaps

**CLI contract:**
- What's not tested: Exact output, module invocation, installed console-script behavior, exit status, stderr, and exceptions.
- Files: `src/mini_claude_code/cli.py`, `src/mini_claude_code/__main__.py`, `tests/test_smoke.py`, `pyproject.toml`
- Risk: User-visible regressions and broken packaging can pass the current suite.
- Priority: High

**Packaging and supported Python versions:**
- What's not tested: Wheel/sdist construction, clean installation, package contents, minimum Python 3.11 compatibility, and dependency resolution.
- Files: `pyproject.toml`, `src/mini_claude_code/`, `tests/test_smoke.py`
- Risk: Local editable installs can work while distributable artifacts or the declared minimum runtime fail.
- Priority: Medium

**Security invariants for future tools:**
- What's not tested: Workspace escape, path traversal, symlink escape, shell metacharacters, destructive-command confirmation, timeout, output bounds, and secret redaction.
- Files: `learning/chapter-template.md`, `src/mini_claude_code/`, `tests/`
- Risk: Tool functionality can be introduced without a regression barrier for the highest-impact agent-harness failures.
- Priority: High

**Chapter workflow integrity:**
- What's not tested: Required chapter files, completed evidence, commit/tag correspondence, and naming conventions.
- Files: `AGENTS.md`, `README.md`, `learning/README.md`, `learning/chapter-template.md`
- Risk: The repository can cease to meet its learning objective even while Python tests pass.
- Priority: Medium

**Coverage measurement:**
- What's not tested: No branch or line coverage threshold is configured, and the two smoke tests cover only package version and direct CLI invocation.
- Files: `pyproject.toml`, `tests/test_smoke.py`
- Risk: Coverage can decline invisibly as the evolving implementation grows.
- Priority: Medium

---

*Concerns audit: 2026-07-19*
