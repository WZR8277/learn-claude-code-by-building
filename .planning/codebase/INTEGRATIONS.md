# External Integrations

**Analysis Date:** 2026-07-19

## APIs & External Services

**Model Provider:**
- Anthropic - Intended model provider for the future mini Claude Code agent loop.
  - SDK/Client: `anthropic>=0.25.0`, declared in `pyproject.toml`.
  - Auth: Local model credentials are expected through `.env` according to `README.md`; the repository does not currently identify or consume a credential variable in `src/mini_claude_code/`.
  - Current state: Dependency declaration only. `src/mini_claude_code/cli.py` prints a baseline status message and performs no network request.
  - Implementation rule: Centralize provider client creation and validate required configuration before making the first API call; do not embed credentials in `src/mini_claude_code/`.

**Learning Source:**
- `shareAI-lab/learn-claude-code` on GitHub - Reference curriculum linked from `README.md`.
  - SDK/Client: None; it is documentation input, not a runtime API integration.
  - Auth: Not applicable.

**Learning Records:**
- Feishu Wiki - Intended destination for per-chapter explanations, reflections, tests, and commit evidence, documented in `AGENTS.md` and `learning/README.md`.
  - SDK/Client: Not detected in `pyproject.toml` or `src/mini_claude_code/`.
  - Auth: Not detected.
  - Current state: Workflow convention only; no automated Feishu API integration exists in the repository.

## Data Storage

**Databases:**
- Not detected. `pyproject.toml` contains no database driver or ORM, and `src/mini_claude_code/` contains no persistence code.

**File Storage:**
- Local repository filesystem only.
- Chapter records are organized under future `learning/sXX-short-name/` directories, with `guide.md`, `reflection.md`, and `evidence.md` specified by `learning/README.md`.
- The active package lives under `src/mini_claude_code/`; no runtime file-reading or file-writing behavior is implemented yet.

**Caching:**
- None. No cache client, cache configuration, or in-process cache is present in `pyproject.toml` or `src/mini_claude_code/`.

## Authentication & Identity

**Auth Provider:**
- No user authentication or identity system is implemented.
  - Implementation: The current local CLI entry point in `src/mini_claude_code/cli.py` has no accounts, sessions, tokens, or authorization checks.
- Anthropic API authentication is planned through local environment configuration, but the client and exact environment-variable contract are not implemented in `src/mini_claude_code/`.

## Monitoring & Observability

**Error Tracking:**
- None. No error-reporting or telemetry dependency appears in `pyproject.toml`.

**Logs:**
- Plain standard-output status text via `print()` in `src/mini_claude_code/cli.py`.
- No Python `logging` configuration, structured event schema, trace correlation, metrics, or remote log sink is present.
- Runtime failures currently rely on normal Python exception behavior; no integration boundary wraps or reports provider errors because provider calls do not yet exist.

## CI/CD & Deployment

**Hosting:**
- Not detected. The project is currently a local installable console package configured in `pyproject.toml`.

**CI Pipeline:**
- None detected. No workflow files or deployment configuration are present under `.github/` or at the repository root.
- Chapter completion requires local automated tests and runtime evidence according to `AGENTS.md`, but no external CI service enforces them.
- Chapter commits and matching `sXX-short-name` tags are process requirements in `AGENTS.md`, not a CI/CD integration.

## Environment Configuration

**Required env vars:**
- No environment variable is currently required by executable code in `src/mini_claude_code/`.
- Model-related configuration will be required when the declared Anthropic client becomes active, but exact variable names are not established in runtime code.
- `.env.example` exists at the repository root and should remain the checked-in template without real secret values.

**Secrets location:**
- Local `.env`, documented in `README.md` and excluded by `.gitignore`.
- `AGENTS.md` explicitly prohibits committing secrets, API keys, access tokens, or `.env`.
- No hosted secret manager or encrypted secret store is configured.

## Webhooks & Callbacks

**Incoming:**
- None. There is no HTTP server, route framework, socket listener, or callback handler in `src/mini_claude_code/`.

**Outgoing:**
- None currently. The Anthropic dependency in `pyproject.toml` is not called by the baseline implementation.
- Future provider requests should be treated as the primary outgoing integration boundary and covered with mocked unit tests plus safe runtime evidence, following the chapter definition of done in `AGENTS.md`.

---

*Integration audit: 2026-07-19*
