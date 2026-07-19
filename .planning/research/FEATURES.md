# Feature Research

**Domain:** Chapter-by-chapter Python reconstruction of an educational coding-agent harness
**Project:** Learn Claude Code by Building
**Researched:** 2026-07-19
**Confidence:** HIGH for upstream chapter names, mechanisms, and deltas; MEDIUM-HIGH for proposed local evidence design
**Upstream snapshot:** `shareAI-lab/learn-claude-code` commit `a9cafe953aa714f9cb1171f217d96bd2734bbcc7` (2026-06-27)

## Scope and Interpretation

This document maps the canonical root-level upstream sequence `s01_agent_loop` through `s20_comprehensive`. It does not use the legacy 12-lesson track under `docs/`, `agents/`, or the current `web/` application; upstream explicitly warns that the old and new chapter numbers do not always match.

Two kinds of requirements are deliberately separated:

- **Upstream tutorial behavior** is the mechanism demonstrated by each chapter's `README.en.md` and runnable `code.py`. Upstream optimizes for conceptual clarity and intentionally simplifies production behavior.
- **Local learning evidence** is what this project should add around an independently written, continuously evolving implementation: deterministic automated tests, a safe reproducible demonstration, an explanation of the delta, a learner reflection, and later commit/tag/Feishu evidence. These are local proof requirements, not claims about upstream code.

The classification used below is:

- **Foundational** — introduces a reusable primitive or invariant needed by later chapters.
- **Integrative** — composes existing primitives into a larger operational behavior; it may still introduce a small amount of new state or routing.
- **Capstone** — proves that previously separate mechanisms coexist around one loop.

Complexity estimates apply to an independent, testable implementation in the local evolving package, not to merely running upstream `code.py`.

## Canonical Chapter Capability Map

| Chapter (verified upstream name) | Class | Learner capability after chapter | Delta from previous chapter | Dependencies | Complexity | Observable local learning evidence |
|---|---|---|---|---|---|---|
| **s01_agent_loop — The Agent Loop: One Loop Is All You Need** | Foundational | Explain and implement the minimal model–tool feedback cycle: append the assistant response, execute every returned Bash `tool_use`, append matching `tool_result` blocks, continue on tool use, and stop on a final response. | From s00's importable CLI shell to the first actual agent harness: one Bash tool, conversation messages, model call, stop/continue decision, and result feedback. | Existing CLI seam; injectable/fake model client; safe temporary workdir. | MEDIUM | Unit test with scripted responses proves `user → assistant(tool_use) → user(tool_result) → assistant(final)` ordering and ID correlation; termination test proves no extra model call after final response; safe demo lists files or creates a harmless file in a temporary directory. Learner can trace one complete turn in their own words. |
| **s02_tool_use — Tool Use: Add a Tool, Add Just One Line** | Foundational | Add specialized file and glob tools without changing the loop, using tool schemas plus a name-to-handler dispatch map; handle multiple tool calls in response order. | Replaces hard-coded `run_bash()` with `TOOL_HANDLERS[tool_name](**input)`; expands one Bash tool to Bash/read/write/edit/glob; adds workspace path validation for file tools. Teaching execution remains sequential. | s01 loop and tool-result protocol. | MEDIUM | Contract tests cover schema/handler registration, unknown tools, read/write/edit/glob behavior, path containment, and two tool calls preserving response order. A before/after code explanation identifies dispatch as the only loop-level delta. |
| **s03_permission — Permission: Check Permissions Before Execution** | Foundational | Route every tool call through a three-outcome gate: hard deny, rule-triggered user approval, or direct allow; return denial as a tool result without executing the handler. | Inserts permission checking before s02 dispatch. Adds deny-list checks, rule matching, approval callback, and denial feedback. Upstream warns simple Bash substring matching is demonstrative, not a secure sandbox. | s02 centralized dispatch; injectable approval decision. | HIGH | Deterministic matrix test proves allow executes once, ask+approve executes, ask+deny does not execute, and hard deny never prompts or executes; result still references the original `tool_use_id`. Safe demo uses harmless stand-ins, not destructive commands. Reflection explicitly distinguishes policy gating from filesystem sandboxing. |
| **s04_hooks — Hooks: Hang on the Loop, Don't Write into It** | Foundational | Register and trigger lifecycle extensions for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`, moving permission and logging out of the loop while preserving control semantics. | Refactors s03's inline permission call into a hook registry; adds ordered callbacks, pre-execution blocking, post-execution observation, prompt-time extension, and Stop-hook continuation. | s03 permission behavior; s01 loop lifecycle. | HIGH | Tests prove callback order, a blocking `PreToolUse` prevents handler and `PostToolUse`, successful execution fires post hook once with output, and Stop can cause exactly one controlled continuation. A structural test or code review shows permission is registered as a hook rather than embedded in loop branches. |
| **s05_todo_write — TodoWrite: An Agent Without a Plan Drifts Off Course** | Foundational | Maintain a small in-session TODO list with statuses and expose it as a tool so the model can plan before multi-step execution; detect/remind when work proceeds without updating the plan. | Adds `todo_write`, stateful TODO rendering/validation, system-prompt planning guidance, a rounds-since-update counter, and reminder injection. It is not yet the durable dependency-aware task system of s12. | s02 tool registration; s01 conversation state; optionally s04 hooks for clean reminders. | MEDIUM | Tests validate accepted statuses and list replacement/update behavior, malformed input, reminder threshold/reset, and exact reminder injection without corrupting message ordering. Demo shows pending → in_progress → completed. Learner explains TodoWrite as ephemeral attention support, not orchestration storage. |
| **s06_subagent — Subagent: Break Large Tasks into Small Ones with Clean Context** | Foundational | Delegate a bounded task to a child agent that starts with a fresh `messages[]`, has its own system prompt/round limit, runs tools independently, and returns only a summary/result to the parent. | Adds the `task` tool and nested agent loop; separates parent and child context instead of placing all delegated work into main history. Upstream teaching version is synchronous and guards recursion/round count. | s01 loop; s02 tools; s03/s04 safety semantics for child execution. | HIGH | Fake-model test asserts the child request contains the delegated prompt but none of the parent's unrelated transcript; parent receives one tool result summary rather than the child's full trace; depth/round cap ends runaway delegation; child permission behavior is explicitly tested. Demo delegates repository inspection. |
| **s07_skill_loading — Skill Loading: Load Only When Needed** | Foundational | Discover skill manifests at startup, inject only a compact catalog into the system prompt, and load full `SKILL.md` instructions on demand through a guarded tool. | Adds two-level knowledge loading, a startup registry/catalog, `load_skill`, and traversal-resistant lookup; the agent loop remains unchanged. | s02 tool dispatch; s10 later generalizes prompt assembly, but is not required here. | MEDIUM | Fixture skills prove catalog metadata is visible before loading while full bodies are absent; valid load returns the exact body; unknown name and traversal attempts fail; optional resources remain unloaded until explicitly read. Learner explains token-economical progressive disclosure. |
| **s08_context_compact — Context Compact: Context Will Fill Up, Have a Way to Make Room** | Foundational | Control context growth through a cheap-to-expensive pipeline: trim irrelevant history, replace old tool results with placeholders, persist oversized results with previews, summarize history when thresholds are reached, and react to overflow. | Adds four pre-LLM compression layers plus reactive compaction and an explicit `compact` tool; context is no longer allowed to grow without bound. | Correct s01 message protocol; substantial histories/tool results from s02+; model summarizer abstraction. | HIGH | Unit fixtures prove each layer independently, protected recent/tool-correlation messages survive, oversized output is persisted under a safe data directory, summary preserves an explicit continuation anchor, and reactive compact retries once rather than looping forever. Budget/threshold tests use deterministic token estimation. Demo can force tiny thresholds. |
| **s09_memory — Memory: Compression Loses Details, Keep a Layer That Doesn't** | Foundational | Persist selected durable facts outside the transcript, choose relevant memories for a turn, inject them, extract new memories after turns, and periodically consolidate duplicates. | Adds `.memory/MEMORY.md` index plus topic files, selection/loading/extraction/consolidation around s08 compaction. Memory preserves stable facts that summarization may omit. Upstream chapter's reduced tool set is pedagogical, not a requirement to remove locally accumulated tools. | s08 context lifecycle; s10 later improves prompt assembly; injectable model calls for selection/extraction. | HIGH | Temporary-store tests cover atomic/indexed writes, relevance selection, injection, extraction deduplication, and consolidation; a restart test proves memory survives a new session; compaction test proves a remembered preference remains available after transcript compression. Reflection distinguishes memory from conversation history and tasks. |
| **s10_system_prompt — System Prompt: Assembled at Runtime, Never Hardcoded** | Foundational | Assemble a system prompt from topic-keyed sections and real runtime context, include conditional sections only when relevant, and cache by serialized context with correct invalidation. | Replaces a hard-coded `SYSTEM` string with `PROMPT_SECTIONS`, `assemble_system_prompt`, `get_system_prompt`, and context updates. | s07 skill catalog and s09 memory are natural conditional sections; works with s01 model call. | MEDIUM | Snapshot/section tests prove stable order, always-on sections, conditional memory/skill/team sections, omission when absent, cache hit for unchanged context, and invalidation after state changes. Learner identifies prompt assembly as a projection of runtime state, not the state itself. |
| **s11_error_recovery — Error Recovery: Errors Aren't the End, They're the Start of a Retry** | Foundational | Recover differently from output truncation, prompt/context overflow, and transient API failures using token escalation/continuation, reactive compaction, exponential backoff, retry bounds, and optional fallback model. | Wraps s10's bare model call in typed recovery transitions and persistent recovery state; tools stay unchanged. | s08 reactive compaction; s10 model/prompt boundary; injectable clock/random/model. | HIGH | Scripted exception tests prove: truncation escalates token budget and continues; prompt-too-long compacts then retries; retryable errors use bounded exponential delays; non-retryable errors fail immediately; retry exhaustion is surfaced; fallback is selected only under its configured condition. No test sleeps in real time. |
| **s12_task_system — Task System: Break Big Goals into Small Tasks** | Foundational | Create durable task records, model `pending → in_progress → completed`, enforce `blockedBy` dependencies, claim eligible work, complete it, and reload state across sessions. | Adds a persistent `.tasks/{id}.json` task board and five task tools. This is separate from s05 TodoWrite: durable coordination/dependency state rather than an in-turn checklist. | s02 dispatch; safe persistence; later chapters rely heavily on task identity and ownership. | HIGH | Tests prove monotonic IDs, JSON round-trip, dependency blocking/unblocking, invalid/missing dependencies, claim/complete transitions, owner field behavior, and restart persistence. Graph fixtures include a chain and multiple prerequisites. Learner can contrast TodoWrite and Task System. |
| **s13_background_tasks — Background Tasks: Slow Operations Go to the Background** | Integrative | Dispatch explicitly requested or heuristically slow Bash work asynchronously, return a background ID immediately, safely collect completion, and inject a new `<task_notification>` rather than reusing the old tool-use ID. | Changes execution strategy while retaining the same tool set: Bash gains `run_in_background`; background registry/result store/lock and notification collection are added. | s02 dispatch; s01 next-turn injection; s11 error containment; concurrency-safe shared state. | HIGH | Tests use events/fake executors to prove immediate placeholder return, foreground work can continue, exactly-once completion notification, failure notification, lock-safe collection, and no fabricated/reused tool-use correlation. Demo uses a short controlled command. |
| **s14_cron_scheduler — Cron Scheduler: Producing Work on a Schedule** | Integrative | Validate five-field cron expressions, create/list/cancel recurring or one-shot jobs, persist durable jobs, poll independently, enqueue due prompts, and deliver them through the agent turn boundary. | Adds a scheduler producer, queue processor, cron consumer path, three tools, session-only vs durable jobs, and `.scheduled_tasks.json`. Unlike s13, work is triggered by time rather than an active user/tool call. | s13 background/notification pattern; durable storage from s12; serialized agent-turn access. | HIGH | Fake-clock tests prove matching, invalid expression rejection, one-shot removal, recurring retention, cancellation, durable reload, session-only non-reload, and exactly-once firing per minute boundary. Queue tests prove due prompts enter normal history/agent processing without concurrent model turns. |
| **s15_agent_teams — Agent Teams: One Agent Isn't Enough, Form a Team** | Integrative | Spawn named teammate loops, give them role/task prompts and restricted tools, exchange JSONL mailbox messages, and inject teammate results into the lead's history. | Moves from one agent to one lead plus N teammate threads; adds `MessageBus`, `.mailboxes/*.jsonl`, teammate lifecycle, spawn/send/check tools. Upstream teaching code omits full permission bubbling. | s06 isolated child loops; s12 tasks; s13 concurrency patterns; s10 role prompts. | HIGH | Multi-agent tests with fake models prove unique identity, mailbox append/read ordering, no cross-recipient leakage, lead receipt/injection, teammate completion, and restricted tool exposure. Corrupt/partial JSONL handling is tested. Reflection labels mailbox protocol as teaching design, not a claim about Claude Code internals. |
| **s16_team_protocols — Team Protocols: Teammates Need Agreements** | Integrative | Coordinate request/response workflows with request IDs, typed routing, pending state, shutdown handshake, and plan submission/review; keep idle teammates available for protocol messages. | Replaces loose text-only coordination with `ProtocolState`, typed dispatch, response matching, unified lead inbox consumption, and explicit shutdown/plan message types. Plan approval is a message-flow example upstream, not yet strong execution gating. | s15 identities/mailboxes; s12 task state; deterministic request ID generation. | HIGH | State-machine tests prove request ID/type correlation, mismatched response rejection, pending → approved/rejected/completed transitions, shutdown request/ack sequence, idle teammate receipt, and unified inbox exactly-once routing. A negative test proves approval state alone does not imply task execution unless locally implemented as a later gate. |
| **s17_autonomous_agents — Autonomous Agents: Check the Board, Claim the Task** | Integrative | Let idle teammates scan the shared task board, atomically claim eligible unowned tasks, work, return to idle, respect dependency order, handle shutdown during idle, and preserve identity across compacted context. | Changes assignment from lead-push to teammate pull; adds `WORK → IDLE → SHUTDOWN`, auto-claim, owner conflict rejection, task tools for teammates, inbox injection, and identity reinjection. | s12 persistent task graph; s15 teams; s16 protocol routing; s08 identity-preserving compaction. | HIGH | Controlled concurrency test has two teammates race for one task and proves one winner; blocked work remains unclaimed until dependency completion; lifecycle trace proves work/idle/shutdown transitions; shutdown during idle responds promptly; compressed child context still contains agent identity. Local implementation should use atomic file/update semantics even though upstream teaching synchronization is simplified. |
| **s18_worktree_isolation — Worktree Isolation: Separate Directories, No Conflicts** | Integrative | Create validated Git worktrees, bind a task to one, automatically switch a claiming teammate's tool cwd, audit lifecycle events, and keep/remove worktrees with dirty-state protection. | Adds per-task directory/branch isolation, `worktree` task field, create/bind/keep/remove tools, cwd routing, name validation, and `events.jsonl`. | s12 task IDs; s17 claims/teammates; actual Git repository fixture. | HIGH | Integration tests in a temporary Git repo prove two worktrees use distinct branches/paths, binding does not claim the task, teammate file writes land only in its worktree, invalid names fail, dirty removal is refused, clean removal succeeds, keep preserves it, and audit events are recorded. Tests never touch the developer's real worktree. |
| **s19_mcp_plugin — MCP Tools: External Tools, Standard Protocol** | Integrative | Connect to external tool servers, discover tools dynamically, normalize them into collision-safe `mcp__server__tool` names, merge them with built-ins, invoke through a common handler, surface annotations, and rebuild prompt/tool state after connections change. | Replaces a fixed all-built-in pool with dynamic assembly; adds teaching `MCPClient`, discovery/call, namespace normalization, `connect_mcp`, readOnly/destructive annotations, and removes stale prompt caching. MCP remains lead-only upstream. | s02 dispatch/schema model; s03 permissions for destructive annotations; s10 dynamic prompt/cache invalidation. | HIGH | Fake-server contract tests prove discovery, name normalization/collision handling, built-in preservation, multi-server coexistence, invocation routing/input/result propagation, connection failure isolation, annotations, lead-only exposure, and tool/prompt refresh after connection. Reflection states upstream simulates MCP and omits transports/OAuth/subscriptions/polling details. |
| **s20_comprehensive — Comprehensive Agent: All Mechanisms, One Loop** | Capstone | Run the complete harness with all mechanisms positioned coherently before LLM calls, around tool execution, after turns, and across background/team activity; explain the end-to-end control and data flow. | Restores mechanisms omitted in intermediate teaching chapters and integrates s01–s19: hooks/permissions, TodoWrite, skills, compaction/recovery, background, cron, task/team/protocol/autonomy, worktrees, memory/prompt, and MCP around one loop. No new headline primitive; integration correctness is the feature. | All prior chapters. | HIGH | End-to-end deterministic scenario creates tasks/worktrees, spawns teammates, routes plan approval, claims dependency-safe work, connects fake MCP, runs controlled background work, fires fake-time cron, compacts history, and completes with permissions/hooks observed. Regression suite for s01–s19 remains green. Learner produces a diagram/explanation locating each mechanism relative to the loop and documents deliberate simplifications. |

## Foundational vs Integrative Capability Layers

```text
s00 CLI/package seam
  └─ s01 loop + message/tool-result protocol
      ├─ s02 dispatch ── s03 permission ── s04 hooks
      │    ├─ s05 ephemeral planning
      │    ├─ s06 isolated subagents ── s15 teams ── s16 protocols ── s17 autonomy
      │    └─ s07 skills ─┐
      ├─ s08 compaction ──┼─ s10 runtime prompt ── s11 recovery
      │    └─ s09 memory ─┘
      ├─ s12 durable tasks ── s13 background ── s14 cron
      │         └──────────── s17 autonomy ── s18 worktrees
      └─ s19 MCP extends dispatch + permission + prompt assembly

All branches converge in s20 comprehensive integration.
```

### Foundation boundary

Treat **s01–s12** primarily as foundations, with two qualifications:

- s05 TodoWrite and s06 Subagent are usable features, but their real roadmap value is as primitives reused or contrasted later.
- s09 and s10 are demonstrated with deliberately reduced tool sets upstream. In this local project, the single evolving implementation should preserve earlier capabilities and add the new mechanism; removing tools to mirror a standalone teaching file would violate the local evolution requirement.

### Integration boundary

Treat **s13–s19** as integration-heavy chapters. Each combines earlier primitives with concurrency, persistence, routing, or external boundaries. **s20** is the capstone integration proof. This is also the natural point where unit tests alone become insufficient and controlled integration fixtures are required.

## Feature Dependencies and Roadmap Ordering

Strict numerical order is justified, but the important dependency edges are more specific than “previous chapter required”:

- **s02 depends on s01:** dispatch only makes sense once the tool feedback protocol is correct.
- **s03 → s04:** implement the policy behavior first, then refactor it behind lifecycle hooks so extension and safety are not learned simultaneously.
- **s05 and s12 must remain distinct:** TodoWrite is ephemeral model attention; Task System is persistent shared workflow with dependencies and ownership.
- **s06 → s15:** learn isolated delegation with one parent/child boundary before adding peer identities, mailboxes, and multiple lifecycles.
- **s08 → s09 → s10 → s11:** first manage finite context, then preserve durable facts, then assemble state into prompts, then recover when limits/services fail.
- **s12 → s17 → s18:** persistent task identity precedes autonomous claiming; task ownership precedes task-to-worktree isolation.
- **s13 → s14:** background completion establishes queue/notification concepts before time-driven producers.
- **s15 → s16 → s17:** communication precedes protocols; protocols precede autonomous idle/claim behavior.
- **s02 + s03 + s10 → s19:** dynamic external tools need dispatch, permission semantics, and prompt/tool-pool invalidation.
- **s01–s19 → s20:** the capstone should not introduce untested mechanisms; it should expose composition defects and close integration gaps.

## Feature Landscape

### Table Stakes for Every Local Chapter

| Feature | Why Expected | Complexity | Notes |
|---|---|---|---|
| Explicit goal and previous-chapter delta | The core value is learning causal evolution, not merely accumulating code. | LOW | Name the invariant preserved as well as the mechanism added. |
| One evolving production implementation | Required by project constraints and avoids twenty disconnected samples. | HIGH | Use Git history/tags for snapshots; do not keep runtime chapter copies. |
| Deterministic automated tests for the new mechanism | Live LLM behavior is nondeterministic and cannot be the only proof. | MEDIUM-HIGH | Inject model, clock, approval, filesystem root, subprocess runner, and transport dependencies. |
| Safe reproducible runtime demonstration | Shows the mechanism works through the stable CLI boundary. | MEDIUM | Default to fake/local fixtures; any live API demo is optional and clearly marked. |
| Regression evidence | Later chapters must not silently break earlier mechanisms. | MEDIUM | Run focused chapter tests plus the full accumulated suite. |
| Learner explanation and personal reflection | Independent understanding is an explicit project outcome. | LOW | Capture before generating the Feishu chapter document. |
| Focused commit and `sXX-short-name` tag | Makes evolution inspectable and is part of the local completion protocol. | LOW | Created only after code, tests, demo, and reflection are complete. |
| Feishu child document after completion | The parent wiki is the long-term review index. | MEDIUM | Record goal, mechanism, delta, code path, tests/demo, reflection, and commit/tag evidence. |

### Differentiators of This Reconstruction

| Feature | Value Proposition | Complexity | Notes |
|---|---|---|---|
| Independent implementation rather than transcription | Forces the learner to reconstruct invariants and expose misunderstandings. | HIGH | Use upstream as behavioral reference; avoid line-for-line ports. |
| Evidence-first chapter contracts | Converts “I read it” into observable state transitions and message traces. | HIGH | Each row above supplies the minimum behavioral evidence. |
| Stable seams for deterministic agent testing | Makes permissions, time, retries, concurrency, and external tools testable without danger or flakiness. | HIGH | Establish injection interfaces early; they compound in value from s08 onward. |
| Cross-chapter conceptual contrasts | Prevents conflating superficially similar mechanisms. | MEDIUM | Especially Todo vs Task, transcript vs Memory, Subagent vs Team, background vs cron, hook vs permission. |
| Capstone compatibility matrix | Proves all mechanisms can coexist around the unchanged loop kernel. | HIGH | s20 should verify combinations, not merely tool availability. |

## Deliberate Anti-Features / Non-Goals

| Anti-Feature | Why It Seems Attractive | Why It Is Problematic | Alternative |
|---|---|---|---|
| Twenty runnable source snapshots | Mirrors upstream folder structure and appears easy to compare. | Violates the local one-codebase evolution constraint and encourages copying rather than reconstruction. | Keep one `src/mini_claude_code/`; use one commit/tag per chapter for historical snapshots. |
| Implementing future chapters early | Reduces later refactoring. | Destroys the observable delta and makes learning evidence ambiguous. | Add only enabling seams, not future behavior; defer feature activation to its chapter. |
| Treating live LLM demos as automated tests | Feels realistic. | Nondeterministic, costly, credential-dependent, and hard to diagnose. | Script model responses for tests; retain a separate optional live smoke demo. |
| Production-grade Claude Code clone | Sounds like a stronger final deliverable. | Upstream explicitly teaches simplified harness concepts and does not claim to reveal proprietary internals. | Build a runnable, explainable educational agent and label simplifications. |
| Bash deny-list as a security boundary | Easy to demonstrate in s03. | Upstream explicitly notes substring matching is bypassable through command variants/expansion. | Test it as policy-routing pedagogy; run demonstrations in temporary directories and rely on OS/process isolation for real safety. |
| Full production hook bus, trust governance, session resume/fork, or MCP OAuth/transports | These are adjacent to real coding-agent products. | They are upstream-declared omissions and would swamp chapter causality. | Record as future research topics after s20, not milestone acceptance criteria. |
| Parallel/streaming tool execution in s02 | Upstream appendix discusses it. | The canonical teaching behavior executes multiple calls sequentially; concurrency would obscure dispatch basics. | Preserve order in s02; introduce concurrency only where the local roadmap explicitly scopes it. |
| Embedding/vector database for s09 memory | Appears more advanced. | Upstream's learning mechanism uses Markdown/index plus model-assisted selection; a vector stack adds unrelated complexity. | Use inspectable files and deterministic selector doubles. |
| Pre-creating all Feishu chapter documents | Makes the course look organized early. | Produces empty or fabricated evidence before reflection/tests/commit exist. | Create each child document only when its chapter is actually complete. |
| Publishing secrets, raw prompts with credentials, or unsafe command logs | Simplifies reproduction. | Violates project security constraints. | Redact environment values and use synthetic test data. |

## Verification Strategy by Complexity Band

### MEDIUM chapters: s01, s02, s05, s07, s10

Prioritize pure/unit tests and one CLI demonstration. Keep model behavior scripted. Evidence should show the exact state or message delta introduced in the chapter.

### HIGH single-agent chapters: s03, s04, s06, s08, s09, s11, s12

Add explicit failure-path and invariant testing. Use dependency injection for approvals, model calls, token estimates, filesystems, delays, and child loops. These chapters can cause major rewrites if state and side effects remain global and inseparable.

### HIGH integration chapters: s13–s20

Use deterministic concurrency/time/transport fixtures plus end-to-end traces. Avoid real sleeps, external MCP servers, and mutation of the developer's real Git worktree in automated tests. Assert exactly-once delivery, ownership, routing, cleanup, and restart behavior.

## Minimum Viable Learning Milestone

Because the declared goal is the complete 20-chapter sequence, “MVP” means a trustworthy learning slice, not stopping permanently at a partial agent.

### First runnable slice

- [ ] **s01 Agent Loop** — validates the central thesis that model + tools + feedback loop yields an agent.
- [ ] **s02 Tool Use** — proves the loop is extensible without rewrite.
- [ ] **s03 Permission** — establishes a safety gate before broader demonstrations.
- [ ] **s04 Hooks** — creates the lifecycle extension seam needed to keep later integration manageable.

### Single-agent foundation milestone

- [ ] **s05–s11** — planning, delegation, on-demand knowledge, finite context, durable memory, runtime prompt assembly, and recovery.
- [ ] **s12 Task System** — establishes persistent work state for later coordination.

### Coordination and extension milestone

- [ ] **s13–s19** — asynchronous work, scheduling, teams, protocols, autonomy, Git isolation, and external tool discovery.

### Capstone

- [ ] **s20 Comprehensive Agent** — all prior regression tests plus an integration scenario and learner architecture explanation.

## High-Risk Chapters Requiring Deeper Phase Research

| Chapter | Why high risk | Phase research focus |
|---|---|---|
| s03 | A teaching permission gate can be mistaken for security isolation. | Explicit threat boundary, safe subprocess strategy, approval interface. |
| s04 | Hook return semantics and order can create bypasses or infinite continuation. | Event contract, ordering, exception policy, Stop-loop bounds. |
| s06 | Nested loops invite recursion, context leakage, and permission ambiguity. | Child capability policy, cancellation/round limits, result boundary. |
| s08 | Message mutation can break tool-use/result pairing; token estimates vary by provider. | Protected-message invariants, compaction thresholds, recovery idempotence. |
| s09 | Memory extraction can store secrets or low-quality/duplicate facts. | Eligibility/redaction, storage schema, consolidation policy, deletion. |
| s11 | Retry combinations can multiply cost or loop forever. | Error taxonomy, retry budget, fallback rules, deterministic test matrix. |
| s12 | Persistence and dependency graphs introduce corruption/cycle/concurrency concerns. | Atomic writes, ID allocation, graph validation, migration/recovery. |
| s13–s17 | Threads, queues, inboxes, and ownership create races and duplicate delivery. | Synchronization model, exactly-once/at-least-once semantics, lifecycle shutdown. |
| s18 | Git worktree operations can mutate or delete real work. | Temp-repo test harness, path/name validation, dirty-state and cleanup policy. |
| s19 | Dynamic tools cross trust boundaries and invalidate prompt/tool caches. | MCP abstraction boundary, namespace collisions, annotations/permissions, failure isolation. |
| s20 | Interactions matter more than individual correctness. | Compatibility matrix, serialized model turns, shutdown/cleanup, capstone acceptance scenario. |

## Acceptance Evidence Common to Every Chapter

A chapter is complete only when all of these artifacts exist locally; upstream does not provide this project-specific completion protocol:

1. A chapter note states the verified upstream name, goal, preserved invariant, and exact delta.
2. The new mechanism exists in the single evolving package and is reachable through the stable CLI or an intentionally documented internal seam.
3. Focused automated tests prove the positive path, the most important negative/failure path, and the previous mechanism's invariant.
4. The complete accumulated test suite passes.
5. A safe, reproducible demonstration records input, salient trace/state, and expected observation; live-model use is optional rather than required for deterministic acceptance.
6. The learner records a personal explanation/reflection before documentation synthesis.
7. One focused learning commit and one matching `sXX-short-name` tag exist.
8. Only then is the Feishu child document created and linked from the parent index.

## Sources

Primary sources were inspected directly from the cloned upstream repository at commit `a9cafe953aa714f9cb1171f217d96bd2734bbcc7` and cross-checked between each chapter's English narrative and runnable Python file.

- [Upstream repository and canonical 20-lesson overview](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7)
- [s01 Agent Loop](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s01_agent_loop)
- [s02 Tool Use](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s02_tool_use)
- [s03 Permission](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s03_permission)
- [s04 Hooks](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s04_hooks)
- [s05 TodoWrite](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s05_todo_write)
- [s06 Subagent](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s06_subagent)
- [s07 Skill Loading](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s07_skill_loading)
- [s08 Context Compact](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s08_context_compact)
- [s09 Memory](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s09_memory)
- [s10 System Prompt](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s10_system_prompt)
- [s11 Error Recovery](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s11_error_recovery)
- [s12 Task System](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s12_task_system)
- [s13 Background Tasks](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s13_background_tasks)
- [s14 Cron Scheduler](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s14_cron_scheduler)
- [s15 Agent Teams](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s15_agent_teams)
- [s16 Team Protocols](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s16_team_protocols)
- [s17 Autonomous Agents](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s17_autonomous_agents)
- [s18 Worktree Isolation](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s18_worktree_isolation)
- [s19 MCP Tools](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s19_mcp_plugin)
- [s20 Comprehensive Agent](https://github.com/shareAI-lab/learn-claude-code/tree/a9cafe953aa714f9cb1171f217d96bd2734bbcc7/s20_comprehensive)
- Local project constraints: `.planning/PROJECT.md`, `README.md`, and `AGENTS.md` in `learn-claude-code-by-building`, read 2026-07-19.

## Confidence and Gaps

- **HIGH — chapter inventory, names, deltas, and upstream demo behaviors:** verified directly in all 20 root-level `README.en.md` files and corresponding `code.py` files at a pinned commit.
- **MEDIUM-HIGH — proposed local evidence:** derived from the observable state transitions in upstream, strengthened for deterministic testing and the local completion protocol; exact test module names and API boundaries remain phase-planning decisions.
- **Known gap:** upstream examples frequently use threads and simplified file persistence but do not define production-grade atomicity, cancellation, crash recovery, or delivery guarantees. These must be explicitly chosen during s12–s17 phase research.
- **Known gap:** s19 teaches MCP through a simulated client and explicitly omits real transport/OAuth/subscription details. A real MCP SDK integration is not implied by reproducing the chapter unless separately scoped.
- **Known gap:** the GSD research-plan/classify-confidence seam could not run in this environment because no `node` executable was available. Confidence above is therefore based on pinned primary-source inspection and local cross-checking, not the unavailable classifier command.

---
*Feature research for: Learn Claude Code by Building*
*Researched: 2026-07-19*
