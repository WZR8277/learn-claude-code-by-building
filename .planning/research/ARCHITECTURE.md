# Architecture Research

**Domain:** Chapter-by-chapter Python reconstruction of a coding-agent harness
**Researched:** 2026-07-19
**Confidence:** HIGH for upstream behavior and dependency order; MEDIUM for the proposed local module timing

## Research Basis and Scope

This document separates two kinds of claims:

- **Observed upstream:** behavior present in the current root-level `s01_agent_loop` through `s20_comprehensive` track of `shareAI-lab/learn-claude-code`.
- **Recommended locally:** how to express that progression in the single evolving `src/mini_claude_code/` package without importing later-chapter architecture early.

The upstream repository explicitly identifies the root-level s01-s20 folders as the canonical track, says each chapter assumes the previous chapters, and describes one invariant model/tool-result loop surrounded by progressively added harness mechanisms. It also warns that the teaching implementation intentionally simplifies production concerns such as full hook buses, permission governance, session lifecycle, worktree lifecycle, and real MCP transports. Those scope limits apply to this reconstruction too.

## Standard Architecture

### System Overview

The end-state shape implied by s20 is a modular monolith around one synchronous agent loop, plus opt-in background coordinators. It should not become a distributed system or a framework hierarchy.

```text
Installed command              python -m mini_claude_code
       │                                  │
       └──────────────┬───────────────────┘
                      ▼
               cli.main()                       stable adapter
                      │
                      ▼
          application/session composition       owns one run
                      │
       ┌──────────────┼───────────────────────┐
       ▼              ▼                       ▼
  prompt/context   agent loop            async event intake
  preparation          │                 (later chapters only)
       │                ▼                       │
       │          model client call             │
       │                │                       │
       │        assistant content blocks        │
       │                ▼                       │
       └──────► policy/hooks/dispatch ◄─────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
       built-in handlers     dynamic MCP handlers
              │                   │
              └─────────┬─────────┘
                        ▼
              tool results / notifications
                        │
                        └────────► messages[] ──► next loop cycle

Persistent workspace state (introduced chapter by chapter):
  skills/   .memory/   .tasks/   .mailboxes/   .worktrees/   schedules
```

The control-flow direction is inward from invocation adapters to one composition boundary and one loop. Capability modules provide data and callbacks to the loop; they do not call the CLI. Stores sit behind their owning component. Background workers communicate through queues/mailboxes and must not mutate conversation history without the session coordinator's lock.

### Component Responsibilities

| Component | Owns | Does not own | First justified |
|---|---|---|---|
| `cli.py` | terminal input/output, process exit translation, composing a run | model loop logic, tools, persistence | s00, already present |
| `agent.py` | invariant model → tool-use → tool-result loop and turn result | concrete tools, terminal prompting, storage formats | s01 |
| `model.py` | Anthropic client construction and one model-call boundary | retry policy before s11; message history | s01, extraction optional until duplication appears |
| `tools.py` | tool schemas, handler registry, name lookup/dispatch | permission decisions, CLI I/O | s02 |
| `workspace.py` | canonical workspace root, safe path resolution | process-global `Path.cwd()` lookups scattered across handlers | s02 |
| `permissions.py` | deny/rule/approval decision model | execution itself | s03 |
| `hooks.py` | event registry and ordered callback invocation | chapter-specific hook behavior | s04 |
| `todos.py` | session-local todo list and validation | durable task graph | s05 |
| `subagents.py` | fresh-context child loop, restricted tool view, summary return | recursive delegation unless a later chapter teaches it | s06 |
| `skills.py` | skill catalog scan and on-demand full-content loading | prompt assembly generally | s07 |
| `context.py` | message-size accounting, compaction, transcript/tool-output spill | long-term memory semantics | s08 |
| `memory.py` | memory index, selection, extraction, consolidation, file store | live conversation history | s09 |
| `prompts.py` | deterministic section assembly from runtime context | model calls | s10 |
| `recovery.py` | retry/backoff, model fallback, token escalation and recovery state | normal dispatch | s11 |
| `tasks.py` | durable `Task` records, dependency checks and state transitions | lightweight session todos | s12 |
| `background.py` | background execution records, lock, result notification queue | scheduling policy | s13 |
| `scheduler.py` | cron records, validation, durable registration, firing queue | direct concurrent calls into an unlocked loop | s14 |
| `teams.py` | teammate lifecycle and restricted teammate runtime | protocol correlation details | s15 |
| `mailbox.py` | message envelope and file-backed inbox transport | request/response semantics | s15 |
| `protocols.py` | correlated request state and typed response routing | physical mailbox persistence | s16 |
| `autonomy.py` | WORK/IDLE/SHUTDOWN transitions and eligible-task scan | task persistence | s17 |
| `worktrees.py` | validated worktree lifecycle and task-to-directory binding | task status completion | s18 |
| `mcp.py` | server/tool discovery abstraction, name normalization, dynamic adapters | built-in handler implementations | s19 |
| `runtime.py` | late-stage composition of registries, stores and coordinators | CLI parsing | only when s20 integration makes composition unwieldy |

The local names are recommendations, not claims about upstream files. Upstream uses standalone `code.py` chapters and frequently omits earlier mechanisms to focus a lesson; the local project instead needs cohesive modules because it keeps one canonical implementation.

## Recommended Project Structure

Do not create this entire tree at s01. The tree is the expected s20 destination; each file should appear only at the chapter shown above.

```text
src/mini_claude_code/
├── __init__.py
├── __main__.py              # always: delegate to cli.main
├── cli.py                   # stable console/module application boundary
├── agent.py                 # s01: invariant loop
├── model.py                 # s01 or when a test seam is first needed
├── workspace.py             # s02: workspace-scoped paths
├── tools.py                 # s02: schema + handler registry/dispatch
├── permissions.py           # s03
├── hooks.py                 # s04
├── todos.py                 # s05
├── subagents.py             # s06
├── skills.py                # s07
├── context.py               # s08
├── memory.py                # s09
├── prompts.py               # s10
├── recovery.py              # s11
├── tasks.py                 # s12
├── background.py            # s13
├── scheduler.py             # s14
├── mailbox.py               # s15
├── teams.py                 # s15
├── protocols.py             # s16
├── autonomy.py              # s17
├── worktrees.py             # s18
├── mcp.py                   # s19
└── runtime.py               # s20, only if composition warrants it

tests/
├── test_smoke.py            # preserve both invocation contracts
├── test_agent.py
├── test_tools.py
└── test_<chapter_mechanism>.py
```

### Structure Rationale

- Keep `__main__.py` a two-line delegation shim. The installed console command bypasses it, so putting behavior there would make `python -m` and `mini-claude-code` diverge.
- Keep `cli.main()` stable while its implementation changes from a readiness print to constructing and running the current chapter's application. Both invocation paths continue to converge there.
- Organize by harness responsibility, not by chapter number. Git commits/tags and `learning/sXX-*` preserve history; production modules represent the current coherent system.
- Prefer plain functions and small dataclasses. Upstream's concepts are registries, records, queues, and loops; a class hierarchy would obscure the lesson.
- Pass a `Workspace`/runtime context explicitly once s02 requires path policy. Avoid mutable state created at import time; upstream examples use globals for teaching brevity, but the local tests need isolated instances.
- Do not create generic `utils.py`, `services/`, dependency-injection containers, repository interfaces, or event-bus abstractions before a chapter demonstrates the pressure that requires them.

## Architectural Patterns

### One Loop, Capability Registries

**Observed upstream:** s01 establishes `messages[] → model → assistant blocks → tools → tool_result → messages[]`. s02 replaces a hard-coded Bash call with tool schemas plus `TOOL_HANDLERS`; s19 extends the same pool with namespaced MCP handlers. s20 still runs that same cycle.

**Recommended locally:** keep one `run_agent_turn`/`agent_loop` implementation. Tool growth should change registry construction, not add `if chapter >= ...` branches to the loop.

```python
while True:
    response = model.call(messages, system=system, tools=registry.schemas())
    messages.append(response.as_message())
    if not response.has_tool_use:
        return response
    results = dispatcher.execute_all(response.tool_calls)
    messages.append(tool_results_message(results))
```

The example is deliberately schematic. Add permission and hook interception only in s03/s04, context preparation only in s08, and recovery only in s11.

### Policy and Hooks Around Dispatch

**Observed upstream:** s03 adds a pre-execution permission pipeline. s04 moves extension logic to `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop` hooks while keeping dispatch recognizable.

**Recommended locally:** define one dispatch boundary with this order once the relevant chapters exist:

```text
tool call
  → PreToolUse hooks (permission may return a denial result)
  → handler lookup
  → handler execution
  → PostToolUse hooks
  → normalized tool result
```

Permissions remain a policy component registered into hooks; hooks do not become a second dispatcher. Before s04, call permissions directly so the s03 increment remains visible.

### Progressive Disclosure for Context

**Observed upstream:** s07 injects a cheap skill catalog and loads full skill content only via a tool. s08 applies cheap deterministic compaction before LLM summarization, persists oversized tool output, and retains transcripts. s09 uses the same index/detail split for memory. s10 assembles stable prompt sections from real runtime state.

**Recommended locally:** model all three as distinct operations:

1. Catalog/index generation (small, stable, prompt-visible).
2. Selection based on the current turn/runtime state.
3. Detail loading into the current request or a tool result.

Do not merge skills, memory, and prompt assembly into a single “context manager”; they have different persistence and update lifecycles. `context.py` should transform message history, while `prompts.py` builds the system string.

### Durable Records Plus Explicit State Machines

**Observed upstream:** s12 introduces file-backed task records with `pending → in_progress → completed` and dependency gates. s16 introduces correlated protocol requests with `pending → approved|rejected`. s17 introduces teammate `WORK → IDLE → WORK|SHUTDOWN`. s18 binds tasks to worktree names but deliberately does not auto-complete tasks when worktrees change.

**Recommended locally:** keep these as separate state models with transition functions that validate current state. Sharing IDs or storage helpers is acceptable after repetition, but do not collapse their semantics into a generic state-machine framework.

## Data and Control Flow

### Foreground Request Flow

```text
terminal query
  → cli.main
  → UserPromptSubmit hooks (s04+)
  → append user message
  → inject due async notifications (s13+ / s14+ / s15+)
  → prepare message context (s08+)
  → derive runtime context + assemble system prompt (s10+)
  → model call through recovery wrapper (s11+)
  → append assistant response
  → no tool use? Stop hooks → render text → return to terminal
  → tool use?
       each call → permission/hooks → foreground or background dispatch
       collect protocol-valid tool_result blocks
       append one user-side results message
       repeat
```

The API message protocol is an invariant: every accepted tool-use block must receive a matching result with the original `tool_use_id`, including denials and unknown tools. Background completion is a later, separate notification; it must not reuse the original call ID after the initial “started” result.

### Async Flow

```text
background worker / cron scheduler / teammate
                  │
                  ▼
       thread-safe result queue or mailbox
                  │
                  ▼
        session coordinator wake event
                  │
          acquire agent/session lock
                  ▼
      append notification as user-side content
                  │
                  ▼
             normal agent loop
```

This boundary becomes necessary at s13. Worker threads should execute handlers and publish immutable completion records. Only the foreground/session coordinator appends to `messages`. s14's scheduler writes fired jobs to a queue rather than calling the model inside the scheduler lock. s15's mailbox poller likewise wakes the lead without independently editing history.

### State Ownership

| State | Lifetime | Owner | Persistence |
|---|---|---|---|
| Conversation messages | one interactive session | agent/session object | transcript only when s08 adds it |
| Todo list and nag counter | one session | `todos.py` / session | in memory (s05) |
| Hook registry | one configured runtime | `hooks.py` | none |
| Tool schemas/handlers | one configured runtime; dynamic at s19 | `tools.py` + `mcp.py` | none |
| Recovery counters/current model | one agent-loop invocation | `RecoveryState` | none |
| Memory index/details | cross-session workspace | `memory.py` | `.memory/` (s09) |
| Durable tasks/dependencies/owner/worktree | cross-session workspace | `tasks.py` | `.tasks/*.json` (s12+) |
| Background task status/results | process lifetime | `background.py` | in memory in teaching scope |
| Cron jobs | process or cross-restart | `scheduler.py` | durable subset on disk (s14) |
| Mailboxes | cross-thread/process teaching transport | `mailbox.py` | `.mailboxes/*.jsonl` (s15) |
| Protocol requests | coordinator process lifetime | `protocols.py` | in memory in teaching scope |
| Teammate lifecycle/current worktree cwd | teammate lifetime | `teams.py` / `autonomy.py` | task binding persists, runtime state does not |
| Worktree records/events | workspace lifetime | `worktrees.py` | Git + `.worktrees/events.jsonl` (s18) |

### Core State Transitions

```text
Task:       pending --claim(deps complete, unowned)--> in_progress --complete--> completed
Protocol:   pending --matched typed response----------> approved | rejected
Teammate:   WORK --model stops------------------------> IDLE
            IDLE --message or eligible task-----------> WORK
            IDLE --shutdown request or timeout--------> SHUTDOWN
Background: running --worker publishes result---------> completed --drain--> removed
Cron:       registered --time match-------------------> queued --consume--> fired
Worktree:   absent --create succeeds------------------> active --keep--------> retained
                                                        active --safe remove-> absent
```

Missing task dependencies remain blocking. A worktree binding changes execution directory but not task status. Protocol responses must match both request ID and expected response type; duplicate or unknown responses do not transition state.

## Verified Chapter-by-Chapter Build Order

| Chapter | Observed upstream increment | Dependency it exercises | Recommended local change |
|---|---|---|---|
| s01 Agent Loop | one Bash tool and invariant model/tool-result loop | model API and message protocol | add `agent.py`; call it from `cli.main`; inject/fake model in tests |
| s02 Tool Use | read/write/edit/glob, safe paths, handler map | s01 loop | add `workspace.py` and `tools.py`; no hook system yet |
| s03 Permission | deny, rules, interactive approval before execution | s02 dispatch seam | add `permissions.py`; return denial as a tool result |
| s04 Hooks | lifecycle callback registry around prompt/dispatch/stop | s03 policy behavior | add `hooks.py`; register permission policy rather than rewriting loop |
| s05 TodoWrite | validated in-memory plan plus nag counter | tool registry and prompt guidance | add `todos.py`; keep distinct from durable tasks |
| s06 Subagent | fresh child messages, reduced tool set, bounded turns, summary-only return | reusable loop/dispatch | add `subagents.py`; no recursive task tool |
| s07 Skill Loading | startup catalog and on-demand full skill | prompt + tool result injection | add `skills.py`; scan only configured directory |
| s08 Context Compact | budget, snip, micro-compact, transcript/spill, LLM summary/reactive compact | message-pair invariants and model access | add `context.py`; test tool-use/result adjacency |
| s09 Memory | file index, selection, detail injection, post-turn extraction/consolidation | s08 snapshots and prompt context | add `memory.py`; preserve pre-compaction source for extraction |
| s10 System Prompt | deterministic runtime section assembly/cache | tools, workspace, memory state | add `prompts.py`; derive context from actual state |
| s11 Error Recovery | token escalation/continuation, context retry, 429/529 backoff and fallback model | one model-call seam and compaction | add `recovery.py`; wrap model calls, not loop logic |
| s12 Task System | durable DAG, claim/complete transitions, ownership | tool dispatch and workspace storage | add `tasks.py`; do not replace session todos |
| s13 Background Tasks | thread execution and completion notifications | normal handler execution and loop feedback | add `background.py`; add session lock/queue boundary |
| s14 Cron Scheduler | durable cron records, scheduler queue, auto-wake consumer | s13 async notification pattern | add `scheduler.py`; scheduler never calls unlocked loop |
| s15 Agent Teams | persistent teammate threads and JSONL mailboxes | tasks + async wake + restricted runtimes | add `mailbox.py`, `teams.py` |
| s16 Team Protocols | typed request/response correlation, graceful shutdown, plan review, idle wait | mailbox routing | add `protocols.py`; centralize inbox consumption |
| s17 Autonomous Agents | WORK/IDLE/SHUTDOWN, task scanning and auto-claim | tasks + protocols + teammate runtime | add `autonomy.py`; verify claim result before work |
| s18 Worktree Isolation | validated git worktree lifecycle, task binding, per-teammate cwd | task ownership and autonomous execution | add `worktrees.py`; thread `cwd` explicitly through handlers |
| s19 MCP Plugin | server discovery abstraction and namespaced dynamic tool pool | registry/dispatch and permissions metadata | add `mcp.py`; teaching mock first, real transport out of current scope |
| s20 Comprehensive | all mechanisms recomposed around one loop | every earlier seam | integrate and refactor only repeated composition; add `runtime.py` if needed |

The order is not arbitrary. In particular: permissions require dispatch; hooks abstract existing permission placement; subagents need a reusable loop and restricted registry; context compaction must preserve the tool protocol; recovery needs a single model-call seam; tasks precede autonomous teammates; team protocols require mailboxes; worktree isolation requires task ownership; MCP discovery requires a dynamic registry.

## Refactoring Thresholds

Refactor only when the current chapter creates observable duplication or a testability problem:

- **s01:** extracting `agent.py` is justified immediately because CLI and loop have different responsibilities. A separate `model.py` is justified when tests need a fake model boundary; do not build a provider abstraction for multiple vendors.
- **s02:** create a registry abstraction because the chapter explicitly changes one handler into many. Keep schemas and callables explicit and inspectable.
- **s04:** a hook registry is justified because multiple cross-cutting callbacks now share ordered lifecycle points. Do not introduce a general event bus.
- **s06:** reuse the same loop only if it can accept a model, system prompt, registry, and limits without global mutation. If adapting it would hide the pedagogical difference, a small child-loop wrapper is preferable to a framework.
- **s08-s11:** separate context preparation, prompt assembly, and recovery because they occur at different points around the model call and have independent tests.
- **s12:** introduce durable store helpers for tasks, but avoid a generic repository layer until a second durable record type genuinely shares atomicity requirements.
- **s13-s16:** introduce an explicit session coordinator/lock when asynchronous producers appear. This is the first point global mutable dictionaries become hazardous.
- **s15:** split mailbox transport from team orchestration because s16 adds routing semantics on top of the same transport.
- **s18:** make `cwd` part of execution context rather than a module global, because each teammate may operate in a different worktree.
- **s19:** separate registry assembly from dispatch because tool availability changes after MCP connection.
- **s20:** consider a `Runtime` dataclass/composition root only now, when constructing all registries/stores/coordinators in `cli.py` would otherwise dominate the stable entry point.

## Anti-Patterns

### Chapter Flags in Production Code

**What people do:** add `if stage >= 8` branches or keep dormant s20 components behind flags.

**Why it is wrong:** it implements later architecture early and makes chapter evidence ambiguous.

**Do this instead:** each tagged commit is the current system. Add a component only when its chapter arrives; Git preserves older runnable states.

### Per-Chapter Runtime Copies

**What people do:** reproduce upstream's standalone `sXX/code.py` layout locally.

**Why it is wrong:** the local project explicitly requires one canonical implementation and already uses tags for history.

**Do this instead:** evolve responsibility modules in place and store narrative/evidence in `learning/sXX-*`.

### Import-Time Runtime Construction

**What people do:** construct API clients, create persistence directories, start scheduler threads, and bind `Path.cwd()` while importing modules.

**Why it is wrong:** tests become order-dependent, the workspace cannot vary, and both CLI entry routes are harder to compare.

**Do this instead:** build configuration, workspace, client, registries, and threads inside `cli.main()` or a later composition function.

### One Global Mutable State Bag

**What people do:** put messages, todos, tasks, recovery counters, background results, requests, and teammates in module globals because upstream teaching scripts do.

**Why it is wrong:** these states have different lifetimes and concurrency rules.

**Do this instead:** use a session object for conversation-local state and focused stores/coordinators for durable or asynchronous state.

### Tool Handlers That Own Policy or UI

**What people do:** prompt for permission inside file/Bash handlers or call `sys.exit()` from reusable code.

**Why it is wrong:** subagents, teammates, tests, and background workers need different approval/UI behavior.

**Do this instead:** keep handlers environment-focused; policy intercepts before dispatch and CLI adapters provide approval callbacks.

### Async Producers Mutating `messages`

**What people do:** let cron/background/team threads append directly to the shared conversation.

**Why it is wrong:** ordering becomes nondeterministic and the API can receive malformed tool-result adjacency.

**Do this instead:** publish notifications to a queue/mailbox and let the locked session coordinator inject them between loop cycles.

### Treating Teaching MCP as a Real Transport

**What people do:** infer stdio/SSE/OAuth lifecycle from s19's mock client.

**Why it is wrong:** upstream explicitly scopes out full MCP runtime details; s19 demonstrates discovery, namespacing, and pool assembly.

**Do this instead:** reconstruct the mock/discovery seam in s19 and flag real transport work as separate phase-specific research if ever added.

## Integration Points

### External Boundaries

| Boundary | Integration pattern | Notes |
|---|---|---|
| Anthropic API | injected client/model-call callable | centralize at one seam for fake responses and s11 recovery |
| Local filesystem | workspace-rooted paths and focused stores | distinguish user project files from harness metadata directories |
| Shell/Git | subprocess wrapper with explicit cwd, timeout and captured output | permissions precede execution; worktrees change cwd only after s18 |
| Terminal | `cli.main()` plus injectable input/output/approval callbacks | do not let package internals depend on console launch form |
| MCP (s19) | discovered schemas adapted into namespaced registry entries | mock teaching transport only in this milestone scope |

### Internal Boundaries

| Boundary | Communication | Invariant |
|---|---|---|
| CLI ↔ runtime | direct call | console and module entry routes invoke identical `cli.main()` behavior |
| Agent ↔ model | typed/protocol-adapted request/response | one call seam, recovery wrapper outside provider client |
| Agent ↔ dispatcher | tool-call input / normalized tool-result output | every tool call gets a corresponding result |
| Dispatcher ↔ policy/hooks | ordered callbacks | denial becomes data, not a missing result |
| Prompt/context ↔ session | pure-ish transformations plus explicit transcript store | never split assistant tool-use from user tool-result pairs |
| Teams ↔ tasks | task IDs and validated claim/complete operations | ownership/dependency checks stay in task store |
| Teams ↔ worktrees | task's worktree name resolved to explicit execution cwd | binding does not imply completion |
| Async producers ↔ session | queues/mailboxes and a coordinator lock | only coordinator mutates conversation history |
| MCP ↔ tools | schema/handler adapter with `mcp__server__tool` names | built-ins and discovered tools share dispatch, not transport code |

## Testing Architecture Implications

- Retain the s00 smoke test and add subprocess coverage for both `mini-claude-code` and `python -m mini_claude_code` whenever CLI behavior changes materially.
- Test `agent.py` with scripted fake model responses: final text, one tool round, multiple tool calls, denial, unknown tool, and malformed inputs.
- Test components at their state boundaries: safe-path escape, permission decision, hook order, todo validation, task dependency transitions, protocol correlation, background result drain, cron matching, worktree name validation, and MCP name collisions.
- Use temporary workspace roots; never let tests write `.memory`, `.tasks`, `.mailboxes`, `.worktrees`, or transcripts into the repository root.
- For s13+, make clocks, sleepers, queues, and thread starts injectable enough to avoid real 60-second waits and nondeterministic tests.
- At every chapter, add one integration test proving the newly registered capability is reachable through the same agent loop rather than only testing its helper functions.

## Roadmap Implications

Roadmap phases should follow the verified chapter order, but refactoring work belongs inside the chapter that first creates pressure for it:

1. **Core loop and guarded dispatch (s01-s04):** establish message protocol, workspace boundary, registry, permissions, and hooks.
2. **Single-agent effectiveness and context (s05-s11):** add planning, isolation, knowledge loading, compaction, memory, prompt composition, and recovery.
3. **Durable work and asynchronous execution (s12-s14):** add task DAGs, background execution, scheduling, and a session coordination lock.
4. **Multi-agent coordination (s15-s18):** add mailbox transport, protocols, autonomy, then worktree isolation.
5. **Dynamic capability integration and recomposition (s19-s20):** add MCP pool assembly, then verify all mechanisms compose around the same loop.

Research flags: s08 requires careful API message-pair testing; s09 requires memory quality/safety evaluation beyond storage tests; s13-s18 require deeper concurrency and filesystem race analysis; s19 requires separate research only if replacing the upstream mock with a real MCP transport.

## Sources

Primary upstream sources inspected directly:

- [Repository README and canonical 20-lesson progression](https://github.com/shareAI-lab/learn-claude-code/blob/main/README.md)
- [s01 Agent Loop](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py), [s02 Tool Use](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py), [s03 Permission](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py), [s04 Hooks](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py)
- [s05 TodoWrite](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py), [s06 Subagent](https://github.com/shareAI-lab/learn-claude-code/blob/main/s06_subagent/code.py), [s07 Skill Loading](https://github.com/shareAI-lab/learn-claude-code/blob/main/s07_skill_loading/code.py), [s08 Context Compact](https://github.com/shareAI-lab/learn-claude-code/blob/main/s08_context_compact/code.py)
- [s09 Memory](https://github.com/shareAI-lab/learn-claude-code/blob/main/s09_memory/code.py), [s10 System Prompt](https://github.com/shareAI-lab/learn-claude-code/blob/main/s10_system_prompt/code.py), [s11 Error Recovery](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py), [s12 Task System](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py)
- [s13 Background Tasks](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py), [s14 Cron Scheduler](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py), [s15 Agent Teams](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py), [s16 Team Protocols](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py)
- [s17 Autonomous Agents](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py), [s18 Worktree Isolation](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py), [s19 MCP Plugin](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py), [s20 Comprehensive Agent](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py)

Local sources inspected:

- `.planning/PROJECT.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/STRUCTURE.md`
- `pyproject.toml`, `src/mini_claude_code/cli.py`, `src/mini_claude_code/__main__.py`, and `AGENTS.md`

---
*Architecture research for: Learn Claude Code by Building*
*Researched: 2026-07-19*
