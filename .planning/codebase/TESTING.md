# Testing Patterns

**Analysis Date:** 2026-07-19

## Test Framework

**Runner:**
- Python standard-library `unittest` under the project's Python `>=3.11` requirement from `pyproject.toml`.
- Config: Not detected; discovery uses the conventional `tests/test_*.py` layout, currently `tests/test_smoke.py`.
- `pytest>=8.0` is declared in the optional `dev` dependency group in `pyproject.toml`, but no pytest configuration or pytest-specific test syntax is present.

**Assertion Library:**
- `unittest.TestCase` assertions from the Python standard library. The baseline uses `self.assertEqual(...)` in `tests/test_smoke.py`.

**Run Commands:**
```bash
python -m unittest discover -s tests -v  # Run all tests (documented baseline)
python -m unittest tests.test_smoke -v   # Run the current smoke module
python -m pytest                         # Optional pytest-compatible run after installing .[dev]
```

No watch-mode or coverage command is configured in `pyproject.toml`, `README.md`, or the repository root.

## Test File Organization

**Location:**
- Keep tests in the top-level `tests/` directory, separate from `src/mini_claude_code/`. The only suite is `tests/test_smoke.py`.
- Mirror the application responsibility in the test filename as the package expands; the current repository groups package-version and CLI-entry-point baseline checks together as smoke tests in `tests/test_smoke.py`.

**Naming:**
- Name test modules `test_*.py`, test classes `*Test`, and test methods `test_*`, following `tests/test_smoke.py`.
- Use descriptive behavior names such as `test_package_has_baseline_version` and `test_cli_entry_point_runs` rather than sequence numbers.

**Structure:**
```text
tests/
└── test_smoke.py     # Package metadata and CLI-entry-point baseline
```

Future chapter tests belong under `tests/` and should remain discoverable by `python -m unittest discover -s tests -v`, the command documented in `README.md`.

## Test Structure

**Suite Organization:**
```python
import unittest

from mini_claude_code import __version__
from mini_claude_code.cli import main


class BaselineSmokeTest(unittest.TestCase):
    def test_package_has_baseline_version(self) -> None:
        self.assertEqual(__version__, "0.0.0")

    def test_cli_entry_point_runs(self) -> None:
        main()


if __name__ == "__main__":
    unittest.main()
```

This is the actual pattern in `tests/test_smoke.py`.

**Patterns:**
- Import `unittest` first, separate application imports with a blank line, and import the exact public object under test, as in `tests/test_smoke.py`.
- Group closely related baseline behaviors in a `unittest.TestCase` subclass.
- Annotate every test method with `-> None`.
- Use `self.assertEqual` for exact value contracts; `test_package_has_baseline_version` in `tests/test_smoke.py` checks the package version.
- A bare call currently serves as a no-exception smoke check in `test_cli_entry_point_runs`; add an assertion when output, return value, state, or error behavior becomes contractual.
- Include `if __name__ == "__main__": unittest.main()` so a test module remains directly executable, following `tests/test_smoke.py`.
- No setup or teardown hooks are present. Add `setUp`, `tearDown`, or context-managed resources only when a test needs owned lifecycle state.

## Mocking

**Framework:** Not detected

**Patterns:**
```python
# No mocks exist in the current suite. Directly invoke deterministic code.
def test_cli_entry_point_runs(self) -> None:
    main()
```

The direct-call pattern is from `tests/test_smoke.py`.

**What to Mock:**
- No current code requires mocks. As external model calls are introduced through dependencies declared in `pyproject.toml`, mock or fake the network/client boundary so automated tests remain safe, deterministic, and credential-free.
- Patch objects at the location used by the code under test, and keep the boundary narrow; add concrete patterns to this document once the implementation establishes them.
- Capture stdout when the exact CLI message becomes a contract instead of mocking `main()` itself.

**What NOT to Mock:**
- Do not mock package constants such as `__version__` in `src/mini_claude_code/__init__.py`; assert them directly as `tests/test_smoke.py` does.
- Do not mock the application entry point when testing that it dispatches without error; call `main()` from `src/mini_claude_code/cli.py` directly.
- Do not let unit tests require real API keys, access tokens, or `.env`; `AGENTS.md` requires secrets to remain uncommitted.

## Fixtures and Factories

**Test Data:**
```python
# Current test data is an inline literal tied to the package contract.
self.assertEqual(__version__, "0.0.0")
```

This pattern is in `tests/test_smoke.py`.

**Location:**
- No fixture modules, factories, temporary-file helpers, or shared test base classes exist.
- Keep a one-off scalar expectation inline, as in `tests/test_smoke.py`. Introduce shared fixtures under `tests/` only when multiple test modules use the same structured input.
- Keep reproducible runtime-demonstration output in each chapter's `learning/sXX-short-name/evidence.md`, not in test fixture files, per `learning/README.md` and `AGENTS.md`.

## Coverage

**Requirements:** None enforced. No coverage dependency, configuration, threshold, badge, or CI gate is present in `pyproject.toml` or repository root.

**View Coverage:**
```bash
# Not configured. Install and configure a coverage tool before relying on this command.
python -m pytest --cov=mini_claude_code tests
```

The example command is not currently available from declared dependencies because `pytest-cov` is not listed in `pyproject.toml`.

## Test Types

**Unit Tests:**
- `test_package_has_baseline_version` in `tests/test_smoke.py` is a direct unit assertion over package metadata from `src/mini_claude_code/__init__.py`.
- Keep deterministic mechanism tests fast and isolated under `tests/`, using `unittest.TestCase` until the repository adopts a different explicit convention.

**Integration Tests:**
- The lightweight CLI smoke check in `tests/test_smoke.py` imports `main()` from `src/mini_claude_code/cli.py` and verifies it completes without an exception.
- No subprocess, console-script installation, model API, filesystem, or multi-module integration test exists.
- Add safe, reproducible runtime evidence for each chapter in `learning/sXX-short-name/evidence.md` in addition to automated tests, as required by `AGENTS.md`.

**E2E Tests:**
- Not used. No browser, process-level CLI, live model, or external-service test framework is configured.
- Keep automated tests offline and credential-free unless an explicit opt-in integration-test layer is added.

## Common Patterns

**Async Testing:**
```python
# Not detected: application and tests are synchronous.
```

There are no `async def` functions, event-loop helpers, or `unittest.IsolatedAsyncioTestCase` usages in `src/mini_claude_code/` or `tests/`. When async harness logic is introduced, use the standard-library async test case or explicitly adopt a configured pytest plugin rather than running ad hoc event loops inside tests.

**Error Testing:**
```python
# Not detected. For future unittest error contracts, follow this shape:
with self.assertRaises(ExpectedError):
    operation()
```

No current implementation exposes an error contract and `tests/test_smoke.py` contains no `assertRaises` usage. Add error-path assertions beside each new failure mode rather than relying only on happy-path smoke execution.

---

*Testing analysis: 2026-07-19*
