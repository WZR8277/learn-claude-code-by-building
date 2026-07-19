# Project Research Summary

**Project:** Learn Claude Code by Building
**Domain:** Chapter-by-chapter Python reconstruction of an educational coding-agent harness
**Researched:** 2026-07-19
**Confidence:** HIGH for the upstream sequence and architecture invariants; MEDIUM-HIGH for local implementation safeguards and version-sensitive stack choices

## Executive Summary

This project is a 20-chapter learning reconstruction of the canonical root-level `shareAI-lab/learn-claude-code` sequence, from `s01_agent_loop` through `s20_comprehensive`, built as one continuously evolving Python package. The central upstream fact is that every capability accumulates around one synchronous model/tool-result loop: tools, permissions, hooks, planning, subagents, context management, memory, recovery, durable tasks, asynchronous work, teams, worktrees, and MCP discovery extend that loop without replacing its protocol spine. The roadmap must therefore retain all 20 chapters in verified numerical order, one focused implementation/evidence unit and one matching Git commit/tag per chapter; the five larger bands below are planning groupings, not permission to merge or reorder chapters.

The recommended local implementation is a modular monolith on Python 3.11+ using the low-level synchronous Anthropic Messages API, a small bounded dependency set (`anthropic`, `python-dotenv`, PyYAML beginning at s07, and pytest), standard-library persistence/concurrency, and explicit injected seams for the model, clock, approval, workspace, subprocesses, and external tools. Upstream teaching behavior and local safeguards must remain visibly separate: the former defines the mechanism being learned; the latter adds deterministic offline tests, workspace containment, bounded processes, atomic-ish state transitions, one-writer coordination, secret redaction, and reproducible evidence without claiming these additions are upstream facts or production-grade Claude Code internals.

The dominant risks are protocol corruption, false confidence in permission prompts, loss of causal state during compaction, conflated state lifetimes, races after s13, uncorrelated multi-agent coordination, unsafe worktree/MCP boundaries, blurred chapter history, and demonstrations being mistaken for evidence. Mitigation is architectural and procedural: preserve assistant `tool_use`/user `tool_result` adjacency and IDs, centralize dispatch policy, keep distinct state owners, let only a session coordinator mutate conversation history, test concurrency with events rather than sleeps, use temporary workspaces and Git repositories, keep s19's MCP transport mocked, retain cumulative regression contracts, and require a structured learning evidence record before each chapter is committed, tagged, and documented in Feishu.

## Upstream Facts and Local Safeguards

This distinction is a roadmap invariant, not merely documentation wording.

| Category | Verified upstream fact | Recommended local safeguard/decision |
|----------|------------------------|--------------------------------------|
| Sequence | The canonical root track is exactly `s01_agent_loop` through `s20_comprehensive`; later chapters assume earlier chapters. | Keep 20 ordered roadmap phases. Use five bands only for milestone navigation and shared research themes. |
| Core loop | A synchronous Anthropic Messages API loop appends assistant content, executes every tool call, appends correlated user-side results, and continues based on stop reason. | Put the loop behind an injectable model seam and lock its transcript contract with scripted offline tests from s01 onward. |
| Teaching architecture | Upstream uses standalone scripts and sometimes omits prior mechanisms to isolate a lesson. | Maintain one evolving `src/mini_claude_code/` package; never create runtime chapter copies or remove accumulated capabilities merely to mirror a standalone script. |
| Permissions and tools | s03 demonstrates deny/ask/allow placement; it is not a sandbox. | Add resolved workspace containment, bounded subprocess execution, redacted environment, safe demos, and one policy-wrapped dispatch path across parent/child/background/team/MCP contexts. |
| Concurrency and storage | s12-s18 teach files, JSON/JSONL, threads, queues, mailboxes, and Git worktrees with pedagogical simplifications. | Add explicit state ownership, atomic store operations where needed, one conversation writer, deterministic race fixtures, bounded shutdown, and temporary-repository tests. |
| MCP | s19 uses an in-process teaching client and mock servers to demonstrate discovery and tool-pool assembly. | Keep transport mocked for v1; namespace tools, distrust metadata/results, apply local policy, and defer real MCP SDK/OAuth/transports to a separately researched post-s20 scope. |
| Completion | Upstream demonstrates mechanisms chapter by chapter. | Require local tests, safe demo, learner reflection, focused commit, matching tag, and only then a Feishu child document. |

## Key Findings

### Recommended Stack

Keep the existing `src`-layout package, setuptools backend, stable `mini-claude-code`/`python -m mini_claude_code` CLI convergence, and synchronous programming model. Avoid an agent framework, Claude Agent SDK, database, message broker, asyncio migration, production MCP runtime, or new package manager during s01-s20: each would hide or distract from mechanisms the learner is meant to construct.

**Core technologies:**

- **CPython `>=3.11`:** project runtime and upstream CI floor; do not raise it during the course.
- **Anthropic Python SDK `>=0.117,<0.118`:** low-level synchronous Messages API behind a narrow injectable client boundary. Treat the minor pin as a time-sensitive local 2026 choice and revalidate on upgrades.
- **`python-dotenv >=1.2.2,<2`:** local interactive configuration with `load_dotenv(override=False)`; environment/CI values win.
- **PyYAML `>=6.0.3,<7`:** skill frontmatter from s07 onward, always through `yaml.safe_load`.
- **setuptools `>=68`, pip, and `venv`:** preserve the working package shell and editable-install workflow.
- **pytest `>=9.1,<10`:** deterministic unit, contract, CLI, concurrency, and temporary-Git integration tests; use built-in fixtures rather than a broad plugin suite.
- **Python standard library:** `pathlib`, dataclasses, JSON/JSONL, subprocess, threading, queues, events, datetime, and Git CLI provide the rest of the curriculum's implementation surface.

**Configuration and test policy:**

- Live mode reads `ANTHROPIC_API_KEY` and validated `MODEL_ID`; `ANTHROPIC_BASE_URL` is optional, and `FALLBACK_MODEL_ID` appears only from s11.
- Never commit, print, transcript, or publish secrets. Keep `.env` ignored and `.env.example` sanitized.
- Set explicit provider and subprocess timeouts. At s11, disable SDK retries so harness-level retry behavior is observable rather than multiplied.
- Default tests use scripted model responses and temporary directories. Live-provider tests remain opt-in and never define correctness.
- Record Python and resolved package versions in chapter evidence; change dependencies separately from chapter mechanisms unless the chapter truly requires the change.

### Expected Features

The v1 scope is the complete verified sequence, not a subset. “Must have” therefore includes both the 20 learned mechanisms and the local evidence contract that proves understanding.

**Must have (table stakes):**

- **s01-s20 in strict order:** each roadmap phase names the verified upstream chapter, its preserved invariant, and its exact delta.
- **One evolving implementation:** all production code evolves in `src/mini_claude_code/`; Git commits/tags provide historical snapshots.
- **Behavioral evidence per chapter:** focused positive and failure-path tests plus the accumulated regression suite.
- **Safe reproducible demo:** temporary workspace by default, bounded effects, sanitized inputs/results, optional live model usage.
- **Learner explanation/reflection:** recorded before documentation synthesis and specific enough to expose predictions, surprises, local choices, and upstream simplifications.
- **History and documentation evidence:** exactly one focused chapter commit, one matching `sXX-short-name` tag, and a Feishu child created only after code, tests, demo, reflection, commit, and tag are final.
- **Stable CLI boundary:** installed command and `python -m` continue to converge on `mini_claude_code.cli:main` throughout the evolution.
- **Cumulative capstone:** s20 retains s01-s19 contracts and proves mechanisms compose around the same loop under fault-injected scenarios.

**Should have (competitive learning value):**

- **Independent reconstruction:** derive behavior and failure cases before comparing with upstream rather than transcribing `code.py`.
- **Stable deterministic seams:** model, approval, filesystem root, subprocess, clock/jitter, queues, IDs, and MCP transport are injectable at their chapter of need.
- **Cross-chapter contrasts:** explicitly distinguish TodoWrite vs durable tasks, transcript vs memory, subagent vs team, background work vs cron, permissions vs hooks, and worktree isolation vs semantic conflict resolution.
- **Compatibility matrix at s20:** scenarios cross context, retry, policy, team ownership, worktree cwd, dynamic tools, scheduling, and shutdown boundaries.

**Defer (v2+):**

- Real MCP SDK transports, OAuth, subscriptions, and network lifecycle.
- Production-grade Claude Code clone claims, broad hook governance, session resume/fork, or trust-control systems absent from the tutorial.
- Agent frameworks or Claude Agent SDK, asyncio conversion, databases/vector stores/message brokers, Docker as a prerequisite, and multi-language rewrites.
- Streaming/parallel tool execution in early chapters, production sandbox claims, or pre-created Feishu chapter documents.

### Architecture Approach

The end state is a modular monolith around one synchronous agent loop plus opt-in background coordinators. Invocation adapters compose one session; focused components own tools, policy, context, prompts, persistence, teams, worktrees, and MCP; workers publish immutable events through queues/mailboxes; and exactly one coordinator owns message mutation and model turns. Modules appear only when their chapter creates the need—no dormant future architecture, chapter flags, generic service layers, or “universal manager.”

**Major components and first justification:**

1. **CLI/composition boundary (`cli.py`, optionally `runtime.py` at s20)** — terminal I/O, configuration, exit translation, and runtime construction; no loop or persistence logic.
2. **Agent/model boundary (`agent.py`, small model seam)** — the invariant messages/model/tool feedback loop and one injectable model-call boundary.
3. **Tool execution boundary (`workspace.py`, `tools.py`, `permissions.py`, `hooks.py`)** — workspace paths, schema/handler registry, normalized dispatch, deny/ask/allow policy, and ordered lifecycle interception.
4. **Single-agent capability modules (`todos.py`, `subagents.py`, `skills.py`)** — ephemeral planning, fresh-context delegation, and progressive skill disclosure.
5. **Context/model-call modules (`context.py`, `memory.py`, `prompts.py`, `recovery.py`)** — transcript reduction, durable facts, deterministic runtime prompt projection, and typed bounded recovery; these concerns remain separate.
6. **Durable/async coordination (`tasks.py`, `background.py`, `scheduler.py`)** — validated task DAG transitions, background completion records, scheduled producers, and the one-writer session boundary.
7. **Team coordination (`mailbox.py`, `teams.py`, `protocols.py`, `autonomy.py`)** — transport, identity/lifecycle, typed correlated requests, and atomic eligible-task claiming.
8. **Isolation and dynamic capability (`worktrees.py`, `mcp.py`)** — explicit per-task execution cwd/Git lifecycle and namespaced dynamic tool discovery behind the same dispatch/policy path.

**Architecture invariants:**

- Every accepted tool call produces exactly one result correlated by original ID, including denial, unknown tool, malformed input, and handler failure.
- Assistant tool-use content and the following user tool-result content remain an indivisible protocol unit through compaction, retries, and async injection.
- Capabilities extend registry construction and seams around the loop; they do not create additional loop implementations.
- State owners and lifetimes stay distinct: session TODOs, conversation, durable memory, durable tasks, protocol requests, teammate lifecycle, and worktree bindings are not one generic state model.
- Workers/schedulers/mailbox pollers never mutate `messages` or call the model under their locks; they enqueue records for the session coordinator.
- Execution context, especially workspace root and later per-teammate worktree `cwd`, is explicit rather than captured from global `Path.cwd()`.
- Importing modules has no network, directory-creation, client-construction, or thread-start side effects.
- MCP-discovered tools share normalized dispatch and local policy but not trusted metadata or transport assumptions.

### Learning Evidence Contract

Every chapter is incomplete until all of the following exist and agree:

1. A record of the verified upstream chapter name, goal, preserved invariant, exact delta, and reading/behavior trace.
2. The mechanism implemented independently in the single package and reachable through the stable CLI or a documented internal seam.
3. Focused deterministic tests for the positive path, most important negative/failure path, and preserved prior invariant.
4. The full cumulative suite passing offline.
5. A safe reproducible demonstration recording exact command, relevant environment/version data, sanitized input, expected invariant, summarized actual result, and exit status.
6. A learner reflection written before Feishu synthesis, including at least one prediction, surprise/failure, local decision, and acknowledged upstream simplification.
7. One focused commit and one matching `sXX-short-name` tag, with unrelated/user-owned changes excluded.
8. Only then, a Feishu child document containing the guide, mechanism, code path, tests/demo, reflection, immutable commit/tag evidence, and a parent-index link.

The pre-existing modified `src/mini_claude_code/cli.py` is user-owned dirty work. It must remain excluded from planning/research and future chapter commits until its ownership is explicitly resolved.

### Critical Pitfalls

1. **Breaking the tool-use protocol** — lock down full transcript traces, stop reasons, parallel call ordering, one-to-one IDs, and normalized failure results from s01; rerun the contract after compaction, retries, async work, and s20 composition.
2. **Treating approval as containment** — explicitly label s03 as policy pedagogy, then add local workspace resolution, bounded subprocesses, output/env redaction, harmless temporary demos, and consistent propagation across every runtime.
3. **Corrupting context causality** — separate transcript, spill evidence, memory, tasks, and prompt projection; preserve protocol pairs and a continuation anchor; allow only bounded overflow recovery.
4. **Conflating state lifetimes** — give TODOs, durable tasks, request protocols, teammate lifecycle, and worktree binding separate schemas, owners, transitions, and restart behavior.
5. **Adding concurrency without one writer/owner** — from s13, workers only publish immutable records; one coordinator owns messages/model turns; use atomic claims and deterministic event/barrier tests.
6. **Mistaking conversation for coordination** — from s15-s17 require stable identities, recipient routing, unique request IDs, expected response types, exactly-once inbox consumption, restricted tools, and explicit shutdown acknowledgment.
7. **Overstating worktree or MCP isolation** — worktrees isolate directories, not semantic conflicts; MCP metadata/results are untrusted. Use explicit cwd, Git lifecycle safeguards, namespacing, policy, consent, and offline mocks.
8. **Losing chapter causality/evidence** — never prebuild future mechanisms, duplicate chapter runtimes, combine chapters in a commit, include unrelated dirty changes, or publish Feishu material before immutable evidence exists.
9. **Using s20 as a rewrite license** — make s20 recomposition and cross-mechanism verification, retaining earlier contracts and refactoring only demonstrated composition duplication.

## Implications for Roadmap

The roadmap should contain **20 sequential phases**, one per upstream chapter, grouped under five bands for navigation. Do not collapse a band into one implementation phase: the project's learning value depends on the observable delta, evidence, commit, and tag at every chapter boundary.

### Band 1: Core Loop and Guarded Dispatch (Phases 1-4)

#### Phase 1: s01 Agent Loop
**Rationale:** Establishes the protocol spine every later feature must preserve.
**Delivers:** Injectable synchronous model loop, one bounded Bash execution seam, exact assistant/tool-result transcript behavior, final-response termination.
**Evidence:** Scripted `user → assistant(tool_use) → user(tool_result) → assistant(final)` trace, multiple-call ordering, errors, no extra call after final, safe temp-workspace CLI demo.
**Avoids:** Chat-loop substitution, live-model-only correctness, unsafe unrestricted demo execution.

#### Phase 2: s02 Tool Use
**Rationale:** Generalizes execution only after the loop is correct.
**Delivers:** Workspace-rooted read/write/edit/glob/Bash tools, schemas, registry, name-to-handler dispatch, normalized unknown/error results.
**Evidence:** Registration contracts, sequential multiple calls, traversal/symlink containment, timeout/output bounds.
**Avoids:** Loop branches per tool, lexical-only path checks, policy or terminal UI inside handlers.

#### Phase 3: s03 Permission
**Rationale:** Policy requires the centralized dispatch seam from s02.
**Delivers:** Explicit deny/ask/allow outcomes and injectable approval, with denial returned as correlated data.
**Evidence:** Matrix proving hard deny never prompts/executes and approval is scoped to one call.
**Avoids:** Claiming a sandbox, substring deny-list as containment, policy drift across execution contexts.

#### Phase 4: s04 Hooks
**Rationale:** Refactors already-working permission behavior into lifecycle extension points without changing semantics.
**Delivers:** Ordered `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop` hooks; permission registered at the pre-use seam.
**Evidence:** Order, blocking, exception isolation, exactly-once post behavior, bounded Stop continuation.
**Avoids:** A second dispatcher, hook recursion, infinite continuation, future event-bus overdesign.

### Band 2: Single-Agent Effectiveness and Context (Phases 5-11)

#### Phase 5: s05 TodoWrite
**Rationale:** Adds ephemeral attention support before durable orchestration, making the later contrast teachable.
**Delivers:** In-session validated TODO state, rendering, planning guidance, and bounded reminders.
**Avoids:** Persisting TODOs or treating them as task ownership/dependency truth.

#### Phase 6: s06 Subagent
**Rationale:** A reusable loop and restricted dispatch now exist; isolated delegation must precede teams.
**Delivers:** Fresh child context, bounded rounds/depth, restricted tools/policy, summary-only parent result.
**Avoids:** Parent transcript leakage, unbounded recursion, child safety bypass, hidden full-trace injection.

#### Phase 7: s07 Skill Loading
**Rationale:** Introduces progressive disclosure before context pressure is formalized.
**Delivers:** Safe manifest discovery, compact catalog, on-demand full `SKILL.md` loading; first PyYAML use.
**Avoids:** Full-body prompt injection, unsafe YAML, traversal, treating loaded external text as trusted policy.

#### Phase 8: s08 Context Compact
**Rationale:** The transcript has enough mechanisms to make context limits real; compaction must precede memory and recovery.
**Delivers:** Budgeting, deterministic reductions, spill/transcript storage, bounded summarization/reactive compact, explicit compact tool.
**Avoids:** Orphaned protocol blocks, lossy continuation state, repeated unbounded overflow retries.

#### Phase 9: s09 Memory
**Rationale:** Durable facts solve a different problem than transcript compression and depend on that distinction being visible.
**Delivers:** Inspectable index/topic files, relevance selection, post-turn extraction, deduplication/consolidation, restart persistence.
**Avoids:** Promoting secrets, untrusted instructions, guesses, or tasks into durable memory.

#### Phase 10: s10 System Prompt
**Rationale:** Skills and memory now provide conditional runtime state worth projecting into a deterministic prompt.
**Delivers:** Ordered topic sections, conditional assembly, context-derived cache key, invalidation on state changes.
**Avoids:** Prompt owning state, global hard-coded system strings, stale caches, injecting every catalog/detail.

#### Phase 11: s11 Error Recovery
**Rationale:** A single model boundary, compaction, and prompt construction now exist, enabling typed recovery without loop rewrites.
**Delivers:** Output continuation/token escalation, prompt-overflow compaction retry, bounded backoff/jitter, typed non-retryable failure, configured fallback.
**Avoids:** SDK and harness retry multiplication, real sleeps, infinite retries, duplicate ambiguous side effects.

### Band 3: Durable Work and Async Execution (Phases 12-14)

#### Phase 12: s12 Task System
**Rationale:** Durable task identity/dependencies must exist before schedules, teams, claims, and worktrees can coordinate around it.
**Delivers:** File-backed task records, dependency validation, claim/complete transitions, ownership, restart/corruption handling.
**Avoids:** Replacing TodoWrite, non-atomic read/write claims, invalid/cyclic dependency ambiguity, one global state file.

#### Phase 13: s13 Background Tasks
**Rationale:** This is the first concurrency chapter and therefore the correct point to introduce the one-writer session boundary.
**Delivers:** Background records, immediate started result, immutable completion queue, safe notification injection, bounded cleanup.
**Avoids:** Workers mutating messages, reused tool-use IDs, duplicate delivery, sleep-based tests, locks across model calls.

#### Phase 14: s14 Cron Scheduler
**Rationale:** Reuses s13's event-intake pattern while changing the producer from an active call to time.
**Delivers:** Cron validation, session/durable jobs, fake-clock matching, due-job queue, cancellation/reload, exactly-once minute firing.
**Avoids:** Scheduler calling the loop while locked, nondeterministic wall-clock tests, duplicate firings, conflating background with scheduled work.

### Band 4: Multi-Agent Coordination and Isolation (Phases 15-18)

#### Phase 15: s15 Agent Teams
**Rationale:** Builds from subagent isolation, durable tasks, and concurrency ownership before adding formal protocols.
**Delivers:** Stable teammate identities, restricted runtimes, JSONL mailbox transport, lead injection, lifecycle/shutdown groundwork.
**Avoids:** All-powerful inherited tools, recipient leakage, multiple inbox consumers, unsupported claims about production internals.

#### Phase 16: s16 Team Protocols
**Rationale:** Formal coordination should layer on a proven mailbox transport.
**Delivers:** Typed envelopes, request IDs, expected response routing, pending transitions, plan review, shutdown request/ack.
**Avoids:** Parsing durable decisions from prose, duplicate/stale response transitions, confusing approval with task completion.

#### Phase 17: s17 Autonomous Agents
**Rationale:** Pull-based work needs durable tasks, team identity, and typed lifecycle control.
**Delivers:** WORK/IDLE/SHUTDOWN loop, eligible task scan, atomic claim, dependency enforcement, idle responsiveness, identity-preserving compaction.
**Avoids:** Two winners, model-decided eligibility, stale owners, lost identity, daemon threads without bounded shutdown.

#### Phase 18: s18 Worktree Isolation
**Rationale:** Task ownership and autonomous execution must precede binding execution to isolated Git directories.
**Delivers:** Validated worktree lifecycle, unique branch/path, task binding, explicit per-runtime cwd, dirty/locked removal refusal, audit events.
**Avoids:** Touching the real repository in tests, direct directory deletion, default force, confusing binding/isolation with completion or semantic merge safety.

### Band 5: Dynamic Tools and Capstone (Phases 19-20)

#### Phase 19: s19 MCP Plugin
**Rationale:** Dynamic external tools require mature registry, policy, and prompt invalidation seams.
**Delivers:** In-process mock client, discovery, collision-safe `mcp__server__tool` names, built-in preservation, normalized invocation/results, dynamic registry/prompt refresh.
**Avoids:** Real transport scope creep, bare-name collisions, trusting annotations/descriptions/results, credential/network requirements.

#### Phase 20: s20 Comprehensive
**Rationale:** All primitives exist; the remaining feature is proof of coherent composition, not a new headline abstraction.
**Delivers:** Small composition root if warranted, cumulative regression suite, safe offline end-to-end trajectory, cross-mechanism fault matrix, architecture explanation, complete history/evidence audit.
**Avoids:** Wholesale rewrite, universal manager, deletion of earlier contracts, final-text-only tests, unbounded threads/retries, hidden cleanup or side-effect duplication.

### Phase Ordering Rationale

- Dispatch follows the loop; permission follows dispatch; hooks abstract established permission placement.
- Ephemeral planning precedes durable tasks so their purposes remain distinct; subagent isolation precedes team identity and mailboxes.
- Compaction precedes memory, prompt projection, and recovery; recovery wraps a stable model-call seam.
- Durable task IDs precede asynchronous/task coordination, autonomous claims, and worktree binding.
- Background notification ownership precedes cron and team concurrency; mailbox transport precedes typed protocols; protocols precede autonomous idle/claim behavior.
- Worktrees follow ownership because isolation must bind a known task/runtime; MCP follows registry, permission, and prompt invalidation.
- s20 consumes all prior contracts and should push any discovered defect back to the seam/chapter that owns it.

### Research Flags

Phases likely needing `$gsd-plan-phase --research-phase <N>` or equivalent focused research at planning time:

- **Phases 1-4:** provider message/result ordering, stop reasons, execution containment, approval semantics, hook ordering/failure/continuation bounds.
- **Phase 6:** child capability inheritance, depth/cancellation/result boundary.
- **Phases 8-11:** token estimation, protected transcript units, memory eligibility/redaction, provider error taxonomy, retry/fallback idempotence.
- **Phases 12-14:** atomic persistence/claim semantics, corruption recovery, exactly-once event delivery, fake-time scheduling, shutdown.
- **Phases 15-18:** JSONL partial writes, correlated protocol routing, deterministic races, lifecycle cleanup, Git worktree porcelain and dirty-state behavior.
- **Phase 20:** explicit cross-mechanism compatibility matrix and fault scenarios discovered from the implemented seams.

Phases with established patterns where research can be light or skipped if upstream remains pinned:

- **Phase 5:** small validated session-local TODO state.
- **Phase 7:** local catalog plus on-demand safe file loading.
- **Phase 10:** deterministic prompt-section assembly and cache-key tests, although cache invalidation inputs need review.
- **Phase 19:** the upstream mock discovery/adapter pattern is sufficiently documented for current scope. If real MCP transport is added, stop and run a separate research phase.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | The minimal-stack direction is strongly supported by upstream imports and official docs; exact 2026 package versions and SDK behavior are time-sensitive and must be revalidated before dependency changes. |
| Features | HIGH | All 20 root-level chapter names, mechanisms, deltas, and dependency edges were checked at pinned upstream commit `a9cafe953aa714f9cb1171f217d96bd2734bbcc7`. Local evidence details are MEDIUM-HIGH pending concrete APIs. |
| Architecture | HIGH for invariants; MEDIUM for module timing/names | One loop, registry growth, distinct state owners, and dependency order are consistent across upstream. Proposed local files are recommendations and must appear only when current pressure warrants them. |
| Pitfalls | HIGH for protocol/scope risks; MEDIUM-HIGH for safeguards | Core protocol and trust-boundary risks are backed by official provider/Python/Git/MCP sources. Atomicity, one-writer coordination, and deterministic-race guidance are local engineering safeguards beyond upstream teaching guarantees. |

**Overall confidence:** HIGH for roadmap construction and scope; MEDIUM-HIGH for implementation details that depend on versions, persistence guarantees, and concurrency choices.

### Gaps to Address

- **Current dependency resolution:** verify installed Python/SDK versions and decide whether to add a constraints/lock artifact before s01 evidence; do not churn package tooling chapter by chapter.
- **Exact local API seams:** phase plans must choose small concrete types/functions for model responses, dispatch results, execution context, and stores without prebuilding future chapters.
- **Provider protocol drift:** recheck official Anthropic tool-use/result and error behavior when s01, s08, and s11 begin or when upgrading the SDK.
- **Persistence guarantees:** upstream does not specify production atomicity, schema migration, crash recovery, or delivery guarantees. Define the minimal local contract at s12-s17 and test it explicitly.
- **Memory quality/safety:** s09 needs eligibility, redaction, deletion/correction, and consolidation criteria in addition to storage tests.
- **Real MCP:** intentionally unresolved and out of v1 scope; requires separate versioned SDK/transport/auth/consent/security research if ever authorized.
- **Feishu automation:** documentation timing and required fields are known, but API permissions, idempotent update behavior, and redaction automation should be verified before first publication workflow.
- **Dirty CLI modification:** resolve ownership of the existing `src/mini_claude_code/cli.py` change before s01 so it is not accidentally incorporated into chapter history.

## Sources

### Primary (HIGH confidence)

- [Pinned upstream repository and canonical 20-lesson overview](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7) — verified s01-s20 names, sequence, narratives, and runnable teaching implementations.
- [Anthropic tool-use loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) and [tool-result handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) — stop reasons, message adjacency, result correlation, errors, and untrusted tool data.
- [Official Anthropic Python SDK documentation](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python) — client, authentication, retries, error categories, and timeout behavior.
- [Python 3.11 subprocess documentation](https://docs.python.org/3.11/library/subprocess.html) and [pathlib documentation](https://docs.python.org/3.11/library/pathlib.html) — timeout/shell responsibility and resolved-path semantics.
- [Git worktree documentation](https://git-scm.com/docs/git-worktree.html) — lifecycle, dirty/locked safeguards, repair/prune, and porcelain output.
- [MCP Tools specification](https://modelcontextprotocol.io/specification/draft/server/tools) and [MCP security principles](https://modelcontextprotocol.io/specification/2025-03-26/index) — discovery, schemas, consent, arbitrary execution risk, and untrusted annotations.
- Local `.planning/PROJECT.md`, mapped codebase documents, `pyproject.toml`, `README.md`, and `AGENTS.md` — project goals, CLI/package baseline, evidence workflow, skill restriction, and dirty-worktree constraint.

### Secondary (MEDIUM confidence)

- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — least privilege, prompt-injection defenses, and logging recommendations.
- Current PyPI package pages and pytest documentation — 2026 version compatibility and built-in fixture strategy; inherently time-sensitive.

### Tertiary (LOW confidence)

- None used for roadmap-defining claims. Any future community pattern for production MCP, crash-safe coordination, or provider-compatible base URLs must be independently validated before adoption.

---
*Research completed: 2026-07-19*
*Ready for roadmap: yes — construct 20 strict sequential phases within the five planning bands above*
