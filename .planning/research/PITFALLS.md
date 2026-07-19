# Pitfalls Research

**Domain:** Chapter-by-chapter Python reconstruction of an educational coding-agent harness
**Project:** Learn Claude Code by Building
**Researched:** 2026-07-19
**Confidence:** HIGH for project/upstream scope and protocol invariants; MEDIUM-HIGH for prevention and recovery recommendations
**Upstream basis:** Canonical root-level `s01_agent_loop` through `s20_comprehensive`, cross-checked against the project research pinned to upstream commit `a9cafe953aa714f9cb1171f217d96bd2734bbcc7` (2026-06-27)

## Critical Pitfalls

### Pitfall 1: Implementing a chat loop instead of the tool-use protocol

**What goes wrong:**
The implementation calls the model repeatedly but fails to preserve the precise conversation structure that makes it an agent loop. Common variants include stopping whenever text is present despite a `tool_use` stop reason, executing only the first tool call, placing tool results in an assistant message, losing the original `tool_use_id`, inserting a notification between a tool call and its result, or failing to return a result for denials, unknown tools, and handler failures. The harness may work for one happy-path demo and then fail with API 400 errors, duplicate side effects, or a model that cannot tell whether its action ran.

**Why it happens:**
The loop is visually small, so learners mistake it for incidental glue rather than the protocol spine. Later chapters add hooks, compaction, retries, and asynchronous notifications near the same message list, which makes it tempting to rewrite the loop or append arbitrary messages at unsafe positions.

**How to avoid:**
Treat the assistant `tool_use` message and the immediately following user `tool_result` message as an indivisible protocol unit. Execute every client tool call in the response in defined order, create exactly one correlated result for each call—including policy denials and exceptions—and append all results before the next model request. Drive continuation from the provider stop reason, with explicit handling for non-final reasons such as truncation once s11 arrives. Keep one loop implementation and grow behavior at the model-call, dispatch, context-preparation, and notification seams.

**Prevention test:**
Use a scripted fake model that returns two tool calls followed by final text. Assert exact roles, block ordering, one-to-one IDs, one handler invocation per call, and no extra model call. Add negative paths for unknown tool, denied tool, handler exception, malformed arguments, and a queued async notification; every path must still leave a protocol-valid transcript. From s08 onward, run the same contract suite against compacted histories.

**Warning signs:**
- Tests assert only final stdout, not the message trace.
- Code branches on “response contains text” instead of the stop reason.
- A denial returns early without constructing a `tool_result`.
- Background completion reuses the original tool call ID.
- Compaction or resume produces orphaned `tool_use` or `tool_result` blocks.
- Adding a tool requires changing the loop body rather than registry construction.

**Recovery:**
Freeze feature work. Introduce a provider-neutral transcript fixture and repair the invariant first. Normalize every dispatch outcome into a result object, reconstruct corrupted test histories from the last valid pair, and add regression fixtures before restoring hooks, compaction, or async injection.

**Phase to address:**
s01 establishes the invariant; s02-s04 preserve it through dispatch and denial; s08 validates it through compaction; s11 validates retries; s13-s16 validate async notification injection; s20 reruns the complete contract matrix.

---

### Pitfall 2: Mistaking permission prompts for a security boundary

**What goes wrong:**
The local coding agent can read or overwrite files outside the teaching workspace, follow symlinks out of it, interpolate model-controlled strings through a shell, leak environment secrets, run indefinitely, emit unbounded output, or execute destructive commands after a superficial substring check. An approval prompt creates confidence without containment. Child agents, background workers, cron jobs, teammates, and MCP tools may bypass the foreground approval path entirely.

**Why it happens:**
Upstream deliberately simplifies production permission governance. A pedagogical Bash tool and string rules demonstrate where policy belongs, not a secure sandbox. Learners often copy the visible check while omitting capability scoping, resolved-path validation, subprocess limits, and consistent policy propagation to every execution context.

**How to avoid:**
Before s02/s03 demos, define a local capability model: an explicit temporary or configured workspace root; resolved-path containment for every filesystem target; a subprocess wrapper with explicit `cwd`, bounded timeout and captured output; no implicit shell for structured commands where avoidable; redacted environment; and confirmation or hard denial for destructive or open-world effects. Route foreground tools, subagents, background jobs, scheduled jobs, teammates, worktree tools, and MCP handlers through the same dispatch-policy contract. Keep demonstrations harmless and disposable. Treat tool outputs and file contents as untrusted data, never as instructions to the harness.

**Prevention test:**
Attempt `../` traversal, absolute paths, a symlink pointing outside the workspace, shell metacharacters, an oversized-output command, a timeout, secret-like environment values, and destructive stand-ins. Assert no out-of-root mutation, bounded runtime/output, redaction, and identical denial semantics from parent, child, background, teammate, and MCP-originated calls.

**Warning signs:**
- “Safe” means only that `rm -rf` is on a deny list.
- File checks use string prefixes or `PurePath.is_relative_to` without resolving symlinks.
- Handlers call `subprocess.run(command, shell=True)` on model-provided text without a separate containment story.
- Tests run against the real repository or home directory.
- Subagents and workers construct their own handler maps without policy wrappers.
- Approval is granted to a whole agent session rather than a specific bounded capability.

**Recovery:**
Disable mutating tools by default; rotate any possibly exposed credentials; inspect Git and audit logs for out-of-scope effects; centralize execution context and policy; then re-enable one capability at a time after adversarial tests pass. Do not claim that s03 creates a sandbox.

**Phase to address:**
s02 workspace/tool boundary, s03 permission pipeline, s04 hook placement, s06 child restrictions, s13-s15 policy propagation, s18 cwd/worktree containment, and s19 MCP trust boundaries.

---

### Pitfall 3: Letting context reduction corrupt causality or learning state

**What goes wrong:**
Long sessions exceed the model window or become dominated by old tool output. A rushed compactor then deletes the exact evidence needed to continue: tool-use/result pairs, the current goal, failed attempts, file paths, task ownership, agent identity, or unresolved decisions. Summaries are treated as lossless memory; repeated compaction accumulates distortion. Conversely, retaining every transcript, tool output, skill body, memory, task record, and MCP schema in every request makes the chapter appear correct under tiny fixtures but unusable with realistic history.

**Why it happens:**
s07-s10 introduce several context mechanisms close together—skill discovery, compaction, memory, and prompt assembly. It is easy to collapse them into one generic “context manager” or to equate context with durable truth. Token estimation is also approximate, and teaching thresholds may not match the selected model.

**How to avoid:**
Separate four concerns: conversation history, spill/transcript evidence, durable memory, and runtime prompt projection. Apply deterministic cheap reductions first, preserve recent and protocol-critical blocks, spill oversized results with a bounded preview, and summarize only after retaining a continuation anchor. Keep durable tasks and worktree bindings outside conversational summaries. Recompute budgets for every outbound request and allow one bounded reactive compaction retry on provider overflow. Extract memory from the best available pre-compaction source, but only persist stable facts—not untrusted instructions or transient guesses.

**Prevention test:**
Build histories containing parallel tool calls, errors, large outputs, a current task, identity, and an unresolved decision. Force very small budgets. Assert no orphaned protocol blocks, the next action remains reconstructable, durable state is unchanged, spill files remain within a safe metadata directory, and retry terminates. Add a restart test showing memory survives but ephemeral TODOs and conversation-local counters do not.

**Warning signs:**
- A compactor slices the message array by index without parsing block relationships.
- Summary tests check only that it is shorter.
- The same object stores messages, memories, TODOs, and durable tasks.
- Full skill bodies or all MCP tool schemas are injected on every turn.
- The agent repeatedly compacts without escaping an overflow retry loop.
- Identity or task ownership disappears after teammate compaction.

**Recovery:**
Restore from the preserved transcript/spill store; rebuild a minimal continuation state from durable records and recent valid protocol pairs; discard suspect generated memories; and add a golden “continuation anchor” fixture. If no raw evidence was retained, mark the chapter evidence incomplete rather than inventing missing state.

**Phase to address:**
s07 progressive disclosure; s08 compaction and spill; s09 memory boundaries; s10 prompt assembly; s11 overflow recovery; s17 teammate identity after compaction; s19 progressive MCP discovery.

---

### Pitfall 4: Conflating TODOs, durable tasks, messages, and protocol requests

**What goes wrong:**
An in-session checklist is used as a durable work queue, chat messages are treated as task truth, protocol approval is interpreted as task completion, or a worktree binding silently changes task status. Restarts lose work; blocked tasks are claimed; IDs collide; owners overwrite each other; completed tasks regress; and the learner cannot explain which state survives which lifecycle.

**Why it happens:**
s05, s12, s15-s18 all introduce “things to do,” but with different purposes and lifetimes. Generic state-machine abstractions or a single JSON file seem convenient in a teaching project, yet they erase precisely the distinctions the chapters are meant to teach.

**How to avoid:**
Document ownership and persistence before implementation. Keep s05 TODOs session-local attention aids. Make s12 tasks durable records with validated transitions, dependencies, ownership, and atomic writes. Make s16 requests separately correlated, typed protocol state. Make s17 teammate lifecycle runtime state. Treat s18 worktree binding as execution-location metadata only. Reject invalid transitions and missing dependencies explicitly; never infer success from a message or directory operation.

**Prevention test:**
Restart between create/claim/complete operations; verify tasks persist while TODOs do not. Test dependency chains, cycles or invalid dependency references, stale owners, double completion, mismatched protocol response IDs/types, and worktree binding without claim/completion. For every transition, assert old state and new state.

**Warning signs:**
- One `status` enum is shared by TODO, task, request, teammate, and worktree records.
- “Plan approved” automatically marks implementation done.
- Creating or keeping a worktree updates task completion.
- Task eligibility is decided by the model instead of store validation.
- IDs come from counting files without collision protection.
- JSON persistence is overwritten directly and can be truncated on interruption.

**Recovery:**
Stop autonomous claiming. Reconcile records from audit history and Git evidence, introduce explicit schemas/migrations, repair illegal states through a one-off validated recovery tool, and re-enable automation only after restart and transition tests pass.

**Phase to address:**
s05 for TODO semantics; s12 for durable DAG and atomic transition rules; s16 for request correlation; s17 for lifecycle/claim semantics; s18 for task-to-worktree binding.

---

### Pitfall 5: Adding concurrency before establishing one writer and one owner

**What goes wrong:**
Background threads, schedulers, mailbox pollers, and teammate loops mutate shared conversation history or durable task files concurrently. Results arrive twice or disappear; model calls overlap on one session; JSONL lines interleave; two teammates believe they claimed the same task; locks deadlock because a scheduler calls the model while holding one; and tests pass intermittently.

**Why it happens:**
The upstream examples are small teaching implementations. Python’s shared-process ergonomics make a global dictionary and a thread look sufficient. The first demo often runs only one worker, hiding races that appear as soon as s13-s17 compose.

**How to avoid:**
At s13 introduce the concurrency boundary deliberately: workers publish immutable completion records to a thread-safe queue; exactly one session coordinator owns `messages` and model turns. Scheduler and mailbox consumers wake or enqueue work, never call the unlocked loop themselves. Use atomic store operations for task claiming and atomic append/replace strategies for persistent files. Define exactly-once consumption semantics and lifecycle shutdown/join behavior. Inject clocks, executors, queues, and IDs for deterministic tests.

**Prevention test:**
Use barriers/events to force two claimants and two completions to race. Assert one claim winner, one history writer, one delivered notification, and no lock held during a model call. Stress partial/corrupt mailbox lines, cancellation, worker exceptions, restart during a durable write, and shutdown while idle. Repeat race tests enough to expose nondeterminism without real sleeps.

**Warning signs:**
- Any worker thread appends directly to `messages`.
- The scheduler invokes the agent loop from its polling lock.
- A `dict` is described as thread-safe because individual operations appear atomic.
- Tests rely on `sleep()` and timing luck.
- Claim is implemented as separate read-then-write operations without a lock or compare-and-set.
- A completion queue has no drained/delivered marker.

**Recovery:**
Pause asynchronous execution; drain queues into an audit file; reconcile duplicate or missing state; centralize mutations behind the coordinator/store; add deterministic race fixtures; and reintroduce background, scheduler, then team concurrency in that order.

**Phase to address:**
s13 establishes queue/coordinator ownership; s14 scheduler discipline; s15 mailbox safety; s16 exactly-once routing; s17 atomic claims; s20 composition stress tests.

---

### Pitfall 6: Treating multi-agent conversation as coordination

**What goes wrong:**
Teammates exchange persuasive natural language but lack identities, request IDs, typed responses, ownership rules, delivery guarantees, or shutdown handshakes. Replies satisfy the wrong request, plans are “approved” by unmatched text, idle teammates miss control messages, teammates recursively spawn more teammates, and failures are silently summarized away.

**Why it happens:**
s15’s JSONL mailbox is intentionally a teaching protocol, not evidence of a production internal architecture. It is easy to assume that because agents can talk, they coordinate correctly. Human-readable logs mask missing machine-checkable state transitions.

**How to avoid:**
Give each teammate a unique stable identity and restricted runtime. Separate mailbox transport from s16 protocol routing. Every request carries a unique ID and expected response type; only a matching, not-yet-consumed response may transition pending state. Centralize inbox consumption and make delivery exactly once. Preserve idle responsiveness, prohibit unintended recursive team spawning, bound turns/depth, and make shutdown an explicit request/ack lifecycle. Validate task ownership in the task store, never through claims in prose.

**Prevention test:**
Inject out-of-order, duplicate, wrong-recipient, wrong-type, corrupt, and stale messages. Assert they do not transition state. Verify an idle teammate receives shutdown promptly, a child cannot spawn nested teams unless explicitly designed, parent context receives only the intended result, and two teammates cannot own one task.

**Warning signs:**
- Protocol state is reconstructed by parsing free-form mailbox prose.
- One polling function and multiple consumers race over the same inbox.
- Teammates inherit all parent tools and credentials.
- Completion is inferred from a “done” message rather than task-store transition.
- Request IDs are absent, reused, or not checked against expected type.
- Threads are daemonized without a shutdown/join test.

**Recovery:**
Quarantine ambiguous messages, rebuild pending protocol state from correlated records, reset uncertain task ownership to a review-required state, and add a typed envelope/version field before resuming. Keep the mailbox implementation explicitly labeled educational.

**Phase to address:**
s06 child isolation foundations; s15 identity/transport; s16 typed protocols and shutdown; s17 atomic ownership and idle lifecycle; s20 end-to-end team failure tests.

---

### Pitfall 7: Believing worktrees eliminate logical conflicts

**What goes wrong:**
Separate directories prevent direct file clobbering but do not prevent two agents from making incompatible changes, checking out the same branch, editing shared external state, or binding the wrong task. Tools continue using the main repository because `cwd` is global or captured at import time. Cleanup force-removes dirty work, manually deletes directories while leaving Git metadata, or removes a worktree before evidence is captured.

**Why it happens:**
“Isolation” sounds stronger than it is. Upstream also omits complete production worktree lifecycle behavior. Learners may copy Git commands without modeling branch/path identity, dirty-state refusal, audit events, or the distinction between task binding and task completion.

**How to avoid:**
Validate worktree names and derive paths beneath a dedicated root. Use `git worktree` lifecycle commands with explicit repository `cwd`; create a distinct branch or documented detached state; bind task-to-worktree explicitly; and thread execution `cwd` through every filesystem and subprocess handler. Refuse dirty or locked removal in normal flows. Record create/bind/keep/remove events. Treat merging and semantic conflict resolution as separate activities, not solved by isolation.

**Prevention test:**
Use a temporary Git repository. Create two worktrees and assert different branches/paths; run teammate writes and verify they land only in the bound tree; reject traversal names and an already checked-out branch; refuse dirty removal; verify clean removal through Git; and confirm binding changes neither owner nor completion. Never point tests at the developer’s repository.

**Warning signs:**
- Tool handlers call `Path.cwd()` internally instead of receiving execution context.
- Worktree paths accept slashes, `..`, or absolute values.
- Cleanup uses filesystem deletion instead of `git worktree remove`.
- `--force` is the default removal path.
- A “worktree created” event marks a task in progress or completed.
- No test proves where a teammate’s file write actually lands.

**Recovery:**
Stop agents using uncertain cwd; inventory with `git worktree list --porcelain`; preserve dirty trees; use `git worktree repair` or `prune` only after inspection; reconcile branches and task bindings; and recreate audit records. Never clean up by blindly deleting directories.

**Phase to address:**
s12 stable task identity; s17 ownership; s18 full isolation lifecycle and cwd routing; s20 integration/cleanup verification.

---

### Pitfall 8: Treating MCP discovery metadata as trusted capability

**What goes wrong:**
Discovered tools overwrite built-ins, collide across servers, inject misleading instructions through names/descriptions/results, receive blanket approval based on self-declared “read-only” annotations, leak local data to remote servers, hang indefinitely, or leave the model prompt/tool cache stale after connection changes. The learner may also claim to have implemented MCP transport, OAuth, subscriptions, and production security when only the upstream teaching mock/discovery seam exists.

**Why it happens:**
s19 makes external tools look like ordinary registry entries, which is the correct composition idea but can hide the trust and lifecycle boundary. Upstream explicitly scopes out full MCP runtime details. MCP annotations are hints from potentially untrusted servers, not authorization facts.

**How to avoid:**
For this milestone, reconstruct the teaching discovery/adapter seam and label the transport as mock unless a separately researched real client is added. Namespace tools with a stable configured server identifier and reject collisions deterministically. Validate schemas and inputs, bound calls with timeouts, sanitize/contain results as untrusted tool data, retain per-tool policy and human confirmation for sensitive operations, and never derive authorization solely from annotations. Rebuild registry and prompt/cache state when connections change. Do not send workspace content or credentials to a server without explicit scope and consent.

**Prevention test:**
Mock two servers exposing the same tool name, invalid schemas, deceptive annotations, a timeout, a tool error, and instruction-like output. Assert collision-safe names, built-in preservation, policy interception, bounded failure, result normalization, and prompt/registry invalidation after connect/disconnect. Verify no real network or credentials are required by the chapter demo.

**Warning signs:**
- Discovered tools are keyed only by bare tool name.
- `readOnlyHint` bypasses confirmation automatically.
- Server descriptions enter the system prompt as trusted policy.
- Adding/removing a server does not change the current tools array or prompt cache key.
- `.mcp.json` secrets or tokens appear in Git/Feishu evidence.
- Chapter claims include OAuth/transport guarantees that tests never exercise.

**Recovery:**
Disconnect all external servers, rotate exposed credentials, restore the built-in registry, quarantine untrusted results, and reintroduce servers individually behind namespacing and policy. Downgrade documentation claims to the actually demonstrated seam.

**Phase to address:**
s03/s04 policy foundation; s10 prompt cache invalidation; s19 MCP discovery/trust boundary; s20 dynamic registry composition.

---

### Pitfall 9: Copying upstream code instead of reconstructing the mechanism

**What goes wrong:**
The repository contains cosmetically renamed upstream scripts, including global state and pedagogical shortcuts, but the learner cannot explain the call path or derive tests. Copyright/attribution questions aside, direct copying defeats the project’s core learning evidence and imports standalone-chapter structure that conflicts with the one evolving local package.

**Why it happens:**
Upstream provides runnable `code.py` for every chapter, and matching it line-for-line gives immediate green demos. Under schedule pressure, “understand then implement” silently becomes “copy then annotate.” Later refactors obscure provenance and make personal reflection generic.

**How to avoid:**
Use a clean-room learning rhythm: first write the chapter goal, invariant, input/output examples, and delta from the previous tag in the learner’s own words; close upstream; implement against those behavioral notes and local architecture; then reopen upstream for a discrepancy review. Retain source attribution and pin the studied commit. Require tests that are not copied from upstream and a reflection that explains at least one local design choice, one upstream teaching simplification, and one failed hypothesis.

**Prevention test:**
Before coding, the learner traces the mechanism on a blank diagram or pseudocode and predicts failure cases. During review, compare structural similarity and ask whether every nontrivial branch can be explained without looking upstream. The chapter is incomplete if tests merely run the upstream happy path or the reflection could apply to any chapter.

**Warning signs:**
- Local names, function order, comments, literals, and global layout mirror upstream exactly.
- A whole `sXX/code.py` appears before local design notes.
- The learner cannot explain why a tool result uses the user role or why a state persists.
- Reflection summarizes the README but contains no local decision or surprise.
- Production code contains chapter-specific standalone entry points.

**Recovery:**
Preserve the questionable implementation as a reference-only diff, rewrite from behavioral contracts in a fresh local module, and expand reflection with the differences discovered. Do not rewrite published Git history; record the correction transparently in the affected chapter before tagging, or in a dedicated corrective commit if already published.

**Phase to address:**
Every chapter, enforced by the pre-implementation guide and chapter definition of done; audit strongly at s01, s08, s15, and s20 where copying pressure is highest.

---

### Pitfall 10: Losing clean chapter boundaries in a single evolving codebase

**What goes wrong:**
Later mechanisms are implemented early, several chapters share one commit, a chapter tag points at unrelated changes, or old runtime copies are kept beside the current implementation. The final code may work, but Git no longer demonstrates how the harness evolved. Conversely, over-freezing earlier code can prevent necessary refactoring and produce duplicated loops.

**Why it happens:**
The chapters are tightly dependent. While implementing s02, it is tempting to prebuild hooks; while implementing s12, to add autonomy; while integrating s20, to rewrite everything. Existing dirty worktree changes can also be swept into a chapter commit accidentally.

**How to avoid:**
Define each chapter’s observable delta before editing. Maintain one canonical package; use cumulative regression tests and Git tags as historical snapshots. Refactor only when the current chapter creates real duplication/testability pressure, and describe that refactor as part of the delta. Before the single chapter commit, verify the diff, exclude unrelated/user-owned changes, complete tests/evidence/reflection, and confirm the tag targets exactly that commit. Never add `if chapter >= N` runtime flags.

**Prevention test:**
Automate a read-only chapter validator: required record headings/checklist, one matching `sXX-short-name` tag, tag-to-commit correspondence, no duplicate executable chapter trees, and prior contract tests still passing. Manually inspect `git diff`/`git status` before commit, especially the pre-existing `src/mini_claude_code/cli.py` modification.

**Warning signs:**
- Dormant classes for future chapters appear in the current diff.
- A chapter guide describes multiple unrelated mechanisms.
- Production code contains stage flags or duplicated loops.
- Tags are created later from memory rather than at chapter completion.
- The worktree is dirty before the chapter begins and ownership is undocumented.
- Feishu evidence cites a commit that includes unrelated files.

**Recovery:**
Before publication, split work into the intended focused commit sequence without discarding user changes, rerun tests at each reconstructed boundary, and retag. After publication, prefer additive corrective commits and transparent evidence updates over destructive history rewriting. If a historical tag is irreparably broad, document the limitation explicitly.

**Phase to address:**
s00 workflow automation, then every chapter gate; s20 performs a full history/tag/evidence audit rather than becoming a catch-all rewrite.

---

### Pitfall 11: Recording demonstrations instead of evidence

**What goes wrong:**
A chapter is marked complete because one interactive run “looked right.” The exact command, environment, fake/live model boundary, expected behavior, test result, commit hash, tag, or Feishu link is missing. Evidence exposes secrets or cannot be reproduced after dependency updates. The learner’s explanation is generated before implementation and does not match the code.

**Why it happens:**
Agent behavior is nondeterministic and visually persuasive. Screenshots and polished Feishu pages feel more complete than deterministic fixtures. The current dependency ranges are open-ended, and chapter protocol is prose-only, so drift is easy.

**How to avoid:**
Use deterministic fake-model tests as primary behavioral evidence and a bounded local demo as secondary illustration. Record the exact command, relevant environment/version data, sanitized input, expected invariant, actual summarized result, test exit status, commit hash, and tag. Create the Feishu child document only after code, tests, reflection, commit, and tag are final. Keep secrets and raw sensitive prompts/output out of Git and Feishu. Lock or record resolved dependency versions.

**Prevention test:**
Run each chapter’s evidence command in a clean temporary workspace and, periodically, from an installed wheel. A validator checks required fields and Git references. A second reader should reproduce the behavior without private context or live destructive access.

**Warning signs:**
- Evidence is only a screenshot or copied terminal transcript.
- Tests call a live model for correctness.
- “All tests passed” lacks command and exit status.
- Reflection predates the final code or repeats upstream wording.
- Feishu is created before the tag or cites `HEAD` rather than a hash.
- API keys, absolute personal paths, or raw external content appear in artifacts.

**Recovery:**
Invalidate the chapter’s done status, recreate evidence in a sanitized temporary environment, pin the exact commit/tag, correct the reflection, and update rather than duplicate the Feishu child document. Rotate any exposed secret immediately.

**Phase to address:**
s00 establishes the evidence schema and dependency reproducibility; every chapter enforces it; s20 audits all chapter artifacts and final integrated behavior.

---

### Pitfall 12: Treating s20 as proof that all mechanisms compose

**What goes wrong:**
Every component has unit tests, but the comprehensive agent fails when mechanisms interact: compaction separates async tool results, retry duplicates side effects, a teammate inherits the wrong cwd, dynamic MCP tools bypass hooks, scheduler notifications race with shutdown, or prompt caching exposes stale task/team state. s20 becomes a large refactor whose green happy path hides the lost chapter contracts.

**Why it happens:**
Unit tests make local components look complete, while integration state space grows sharply after s12. There is pressure to “clean up” architecture at the capstone, changing too many seams at once.

**How to avoid:**
Make s20 primarily recomposition and verification. Retain one loop, one normalized dispatch path, explicit execution context, one session writer, and focused state owners. Add scenario tests that cross chapter boundaries: denied background tool; compacted teammate session with task ownership; retry after a non-executed model error versus no retry after ambiguous side effect; worktree-bound teammate calling a namespaced MCP tool; scheduler wake during idle; and graceful shutdown with queued notifications. Refactor only demonstrated duplication, with all earlier contract tests retained.

**Prevention test:**
Run the full cumulative suite plus fault-injected end-to-end scenarios in temporary directories and Git repositories. Assert no duplicate side effects, no orphaned protocol blocks, deterministic cleanup, bounded threads/retries, current prompt/tool registry state, and chapter history integrity.

**Warning signs:**
- s20 deletes or rewrites earlier tests instead of adding composition tests.
- A new “universal manager” owns prompts, messages, tasks, threads, and tools.
- Integration tests exercise only final text.
- Retry logic cannot distinguish safe-to-retry model calls from ambiguous tool effects.
- Thread/process cleanup is not asserted.
- The s20 diff is larger than the sum of a small composition root and integration tests without a clear rationale.

**Recovery:**
Bisect by chapter tags and restore the last valid seam; recompose incrementally in the verified roadmap order; preserve failing interaction fixtures; and split architectural cleanup into explicit corrective work rather than hiding it inside the capstone evidence.

**Phase to address:**
s20, with prerequisites established at s01, s03/s04, s08/s11, s13, s17/s18, and s19.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Global mutable state copied from standalone teaching scripts | Minimal code and easy demos | Order-dependent tests, unclear lifetimes, races from s13 onward | Only inside a throwaway spike, never the evolving package |
| One permissive Bash tool using `shell=True` | Matches the conceptual s01 demo | Injection, environment leakage, no structured policy or portability | Only with harmless fixed commands in a disposable demo; not for model-controlled unrestricted execution |
| String-prefix path checks | Simple containment code | `..`, symlink, and sibling-prefix escapes | Never for mutating tools |
| Replacing old tests with current behavior | Smaller suite | Earlier chapter regressions disappear and history loses meaning | Never; update only when the chapter explicitly changes the contract |
| One JSON file for all persistent state | Easy inspection | Lost updates, schema coupling, corruption blast radius | Small single-writer prototypes before concurrency, with atomic replacement |
| `sleep()`-based concurrency tests | Easy to write | Flaky, slow, misses forced interleavings | Only as a bounded smoke test in addition to event/barrier tests |
| Injecting every skill, memory, and MCP schema | Simple prompt assembly | Token growth, stale cache, irrelevant/untrusted context | Tiny deterministic fixtures only |
| Parsing protocol decisions from prose | Human-readable | Ambiguous correlation and unsafe state transitions | Never when the message changes durable state |
| Default `--force` worktree cleanup | Fewer cleanup failures | Silent loss of uncommitted learning work | Never in normal execution; only explicit human-directed recovery after inspection |
| Full real MCP transport in s19 | More impressive demo | Scope explosion into auth, lifecycle, networking, and security | Only as a separately researched milestone |
| Prebuilding future abstractions | Fewer later refactors | Blurred chapter causality and speculative complexity | Only when required to test the current chapter seam |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Anthropic Messages API | Insert text/notifications between assistant tool use and user tool results, or omit error results | Preserve immediate paired messages; correlate every client result by original ID; inject notifications only at safe turn boundaries |
| Python subprocess | Pass model text to an unrestricted shell with no timeout/output bound | Use a constrained wrapper, explicit cwd/environment, structured argv where possible, timeout, bounded capture, and policy before execution |
| Filesystem/pathlib | Check lexical prefixes before access | Resolve workspace and candidate paths, account for symlinks, validate containment at the operation boundary, and test races/links |
| Git worktree | Delete directories directly or force-remove dirty trees | Use Git lifecycle commands, inspect porcelain state, refuse dirty/locked removal, repair/prune only after validation |
| Feishu | Publish polished docs before code/tag evidence exists | Create/update the chapter child only after reflection, tests, commit, and tag are final; store sanitized immutable references |
| MCP server | Trust names, descriptions, annotations, or outputs | Namespace by configured server identity, validate schemas/results, apply local policy and consent, time out calls, treat metadata/content as untrusted |
| Model provider retry | Retry an ambiguous side-effect path indiscriminately | Retry model requests only under typed conditions; make tool effects idempotent where possible and record dispatch state |
| Dependency resolution | Leave broad ranges without recording resolved environment | Lock or constrain tested dependencies and include environment evidence for chapters that depend on SDK behavior |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Unbounded transcript/tool outputs | Increasing latency/cost, overflow, huge evidence files | Budget before each call, spill oversized results, deterministic trimming, bounded summaries | As soon as file listings/test logs become nontrivial; explicitly exercised in s08 |
| Full catalog injection | Prompt dominated by skill/MCP definitions | Catalog/search then load details on demand; stable cache breakpoints | Dozens of tools or several verbose skills, often by s19 |
| Polling loops with fixed real sleeps | Slow tests, shutdown latency, wasted CPU or delayed jobs | Injectable clocks/events, blocking queues, bounded poll intervals | s13-s17 even with one worker |
| Holding locks across model/network calls | Frozen scheduler/team, deadlocks, serialized latency | Copy work under lock, release, then call external systems; single coordinator | First overlapping background/team event |
| Repeated full-directory scans | Latency rises with memories/tasks/worktrees | Maintain small indexes, validate incrementally, compact audit logs deliberately | Hundreds/thousands of records; still worth instrumenting in the teaching scope |
| Duplicate retry side effects | Repeated files/commands/messages after transient errors | Separate model-call retry from tool execution; idempotency keys/status records | Any failure after a side effect but before acknowledgement |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Treating tool/file/web output as trusted instructions | Indirect prompt injection causes unintended tool use or data leakage | Keep it in tool-result/data boundaries, label provenance, restrict tools, require confirmation for sensitive effects |
| Leaking environment or config into model/evidence | API keys and personal data leave the machine or enter Git/Feishu | Minimal allowlisted environment, redaction tests, secret scanning, sanitized evidence |
| Assuming an approval hook is a sandbox | Approved or bypassed calls have host privileges | Defense in depth: workspace containment, process limits, least privilege, audit, and approvals |
| Symlink/path traversal | Read/write outside teaching workspace | Resolve paths and verify containment; reject unsafe names; test symlinks and nonexistent targets |
| Child/worker policy drift | Restricted foreground but powerful subagents/background/MCP | One dispatch-policy contract and explicit per-runtime tool subsets |
| Trusting MCP annotations | Malicious server labels destructive/exfiltrating tool as safe | Treat annotations as hints only; enforce local policy from trusted configuration and user consent |
| Unbounded command/network execution | Resource exhaustion, hangs, large context injection | Timeout, cancellation, output cap, concurrency quota, normalized errors |
| Unsafe worktree cleanup | Loss of uncommitted work | Dirty/locked checks, no default force, event audit, temporary-repo tests |

## Learning-Experience Pitfalls

| Pitfall | Learner Impact | Better Approach |
|---------|----------------|-----------------|
| Starting from upstream code rather than a behavior trace | Produces familiarity without mechanistic understanding | Predict the loop/state transitions first, implement locally, then compare |
| Hiding teaching simplifications | Learner overgeneralizes demo security/concurrency/MCP claims | Label “observed upstream,” “local safety addition,” and “not implemented” separately |
| Over-abstraction early | Learner sees frameworks instead of the chapter mechanism | Keep current delta explicit; refactor only at demonstrated pressure points |
| Flaky live-model evidence | Failures look mysterious and cannot prove correctness | Scripted fake-model contracts first; bounded live demo second |
| Polished documentation without personal falsifiable claims | Reflection becomes generic summary | Require one prediction, one surprise/failure, one local decision, and evidence |
| Chapter copies instead of Git history | Learner compares duplicated snapshots rather than evolution | One evolving package, cumulative tests, one focused commit/tag per chapter |

## “Looks Done But Isn’t” Checklist

- [ ] **s01 loop:** Final text appears, but multiple tool calls, error results, immediate adjacency, and ID correlation are all tested.
- [ ] **s02 tools:** Read/write/edit/glob work, but traversal, symlink escape, unknown tools, timeouts, and output limits are rejected.
- [ ] **s03 permissions:** Prompts appear, but hard-deny/ask/allow semantics and non-foreground runtimes share the same policy contract.
- [ ] **s04 hooks:** Hooks fire, but order, blocking, exception behavior, and exactly-once post/stop semantics are verified without a second dispatcher.
- [ ] **s05 TODOs:** Statuses render, but malformed updates, reminder reset, and session-only lifetime are explicit.
- [ ] **s06 subagent:** Delegation returns text, but child context is fresh, toolset restricted, depth/round bounded, and full child trace is not leaked to parent.
- [ ] **s07 skills:** A manifest loads, but full bodies are absent before selection and traversal/unknown names fail.
- [ ] **s08 context:** History shrinks, but protocol pairs, continuation anchor, current goal, spill containment, and retry bounds survive.
- [ ] **s09 memory:** Files persist, but unstable guesses/untrusted instructions are not promoted and restart/relevance/deduplication are tested.
- [ ] **s10 prompt:** Sections concatenate, but order is deterministic and cache invalidates on actual runtime state changes.
- [ ] **s11 recovery:** Retries happen, but typed errors, retry exhaustion, injected clock, context recovery, and no duplicate side effects are proven.
- [ ] **s12 tasks:** JSON files exist, but transitions, dependencies, atomic claim, ownership, corruption, and restart are tested.
- [ ] **s13 background:** A thread starts, but foreground returns immediately, completion delivers once, failures normalize, and only coordinator mutates messages.
- [ ] **s14 cron:** A job fires, but invalid expressions, exact-once minute boundary, session/durable distinction, restart, and cancellation work with a fake clock.
- [ ] **s15 teams:** Teammates chat, but identity, recipient isolation, restricted tools, mailbox corruption, lifecycle, and lead injection are verified.
- [ ] **s16 protocols:** Requests have IDs, but wrong/duplicate/stale response types cannot transition state and shutdown is acknowledged.
- [ ] **s17 autonomy:** Agents claim tasks, but a forced race has one winner, dependency blocking holds, idle shutdown works, and compaction preserves identity.
- [ ] **s18 worktrees:** Directories differ, but Git branches, explicit cwd routing, dirty refusal, audit events, and binding-vs-completion semantics are verified in a temp repo.
- [ ] **s19 MCP:** Tools appear, but collisions, stale registry/prompt state, untrusted annotations/results, timeouts, consent, and mock-versus-real scope are explicit.
- [ ] **s20 comprehensive:** One demo completes, but cross-mechanism fault scenarios, cleanup, cumulative regression tests, and chapter history/evidence audit all pass.
- [ ] **Chapter evidence:** Tests pass, but the exact command, sanitized result, reflection, commit hash, matching tag, and Feishu child link are present and reproducible.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Broken tool-use transcript | HIGH | Stop new turns; restore last valid pair; normalize all outcomes; add golden protocol fixtures; then re-enable context/async features |
| Unsafe tool boundary or possible secret exposure | HIGH | Disable tools; rotate credentials; inspect audit/Git/Feishu; centralize containment/policy; adversarially retest |
| Lossy/broken context compaction | MEDIUM-HIGH | Restore transcript/spills; rebuild continuation anchor; invalidate suspect memory; rerun overflow fixtures |
| Corrupt/ambiguous task state | HIGH | Pause autonomy; reconcile from audit/Git; migrate schemas; validate transitions and atomic claims before resume |
| Async duplicates/races | HIGH | Quiesce workers; drain/audit queues; reconcile exactly-once state; enforce one writer; deterministic race tests |
| Uncorrelated team protocol | MEDIUM-HIGH | Quarantine ambiguous messages; rebuild pending IDs/types; reset uncertain ownership; version the envelope |
| Dirty/broken worktree lifecycle | MEDIUM-HIGH | Inventory porcelain state; preserve dirty trees; repair links; reconcile task binding; remove only through Git after review |
| Untrusted MCP integration | HIGH | Disconnect; rotate credentials if needed; restore built-ins; quarantine results; re-add one namespaced, policy-bound server at a time |
| Over-copied implementation | MEDIUM | Re-derive behavioral contracts; rewrite independently; document differences; retain transparent attribution/history |
| Blurred chapter history | HIGH if published | Preserve user changes; reconstruct boundaries pre-publication, or add transparent corrective commits and evidence after publication |
| Weak evidence | LOW-MEDIUM | Mark incomplete; rerun deterministic tests/demo in clean temp environment; sanitize and update Feishu references |
| s20 integration collapse | HIGH | Bisect tags; restore last valid seam; add failing interaction fixture; recompose in dependency order |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Chat loop instead of protocol loop | Phase 1: s01-s04; regression at s08/s13/s20 | Golden transcript tests with parallel, denied, failed, compacted, and async cases |
| Permission mistaken for sandbox | Phase 1: s02-s04; propagation s06/s13/s15/s18/s19 | Traversal, symlink, injection, timeout, output, redaction, and child/worker policy matrix |
| Context corruption/growth | Phase 2: s07-s11; identity regression s17 | Tiny-budget fixtures preserve pairs, anchor, state ownership, and bounded retry |
| State-lifetime conflation | Phase 2 s05; Phase 3 s12; Phase 4 s16-s18 | Restart and explicit transition tests for each independent state model |
| Concurrency without ownership | Phase 3: s13-s14; Phase 4: s15-s17 | Barrier races prove one writer, one claim winner, exactly-once delivery, prompt shutdown |
| Conversation mistaken for team protocol | Phase 4: s15-s17 | Typed correlation, recipient isolation, duplicate/stale rejection, shutdown handshake |
| Worktrees mistaken for full isolation | Phase 4: s18 | Temporary-Git integration proves cwd, branch/path isolation, dirty refusal, correct lifecycle |
| MCP metadata trusted | Phase 5: s19 | Collision, deceptive annotation/output, timeout, policy, consent, cache invalidation tests |
| Upstream copied instead of learned | Every chapter | Pre-code behavior trace, independent tests, discrepancy review, specific reflection |
| Chapter boundaries blurred | s00 workflow and every chapter gate | Read-only validator plus manual diff/status/tag review; no runtime chapter flags/copies |
| Demo mistaken for evidence | s00 workflow and every chapter gate | Clean-environment reproduction with command/result/hash/tag/Feishu record |
| Components fail to compose | Phase 5: s20 | Cumulative suite plus fault-injected cross-mechanism scenarios and cleanup assertions |

## Roadmap Research Flags

- **s01-s04:** Deep research is required around the exact provider message protocol and the difference between approval policy and containment. Do not proceed to convenience abstractions until the golden transcript and adversarial tool boundary tests pass.
- **s05-s07:** Standard patterns are sufficient if state lifetimes and progressive disclosure remain explicit. The key review question is whether the learner can explain why TODOs and skills are not durable orchestration state.
- **s08-s11:** Deep research is required. Context budgets, provider errors/stop reasons, summary preservation, and retry safety are highly coupled; preserve raw evidence and inject token estimator/clock/model.
- **s12-s14:** Deep research is required for atomic persistence, exactly-once delivery, cancellation, and scheduler semantics. Teaching code should not be mistaken for crash-safe production coordination.
- **s15-s18:** Deep research is required for mailbox corruption, typed correlation, atomic claims, lifecycle shutdown, and Git worktree behavior. These phases need deterministic race tests and temporary repositories.
- **s19:** The upstream mock/discovery seam is sufficient for this milestone. A real MCP transport would need a separately scoped research phase covering SDK/version, transport, authorization, consent, lifecycle, and network security.
- **s20:** Treat as integration verification, not a license for wholesale architecture replacement. Research any newly discovered interaction failure at the chapter seam that owns it.

## Sources

All external claims were treated as untrusted source data and cross-checked against project-local research where possible.

- [shareAI-lab/learn-claude-code — canonical repository and scope](https://github.com/shareAI-lab/learn-claude-code) — root-level s01-s20 sequence; explicitly identifies simplified/omitted production mechanisms and teaching-only JSONL mailbox semantics. **Confidence: HIGH** for upstream scope when combined with the project’s pinned FEATURES/ARCHITECTURE research.
- [Anthropic: How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) — canonical client tool loop and stop-reason behavior. **Confidence: HIGH** (official provider documentation).
- [Anthropic: Handle tool calls](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls) — immediate adjacency, result-first ordering, ID correlation, error results, and untrusted tool-result guidance. **Confidence: HIGH**.
- [Python 3.11: subprocess](https://docs.python.org/3.11/library/subprocess.html) — shell invocation responsibility, timeout behavior, and pipe/deadlock considerations. **Confidence: HIGH**.
- [Python 3.11: pathlib](https://docs.python.org/3.11/library/pathlib.html) — `Path.resolve()` resolves symlinks/eliminates `..`; pure-path relative checks are lexical. **Confidence: HIGH**.
- [Git: git-worktree](https://git-scm.com/docs/git-worktree.html) — add/list/lock/remove/prune/repair behavior, dirty and locked safeguards, and stable porcelain output. **Confidence: HIGH**.
- [Model Context Protocol: Tools](https://modelcontextprotocol.io/specification/draft/server/tools) — tool discovery/schema, human-in-the-loop guidance, and collision disambiguation. **Confidence: HIGH** for specification requirements; draft status should be pinned if real transport is later implemented.
- [MCP specification: Security principles](https://modelcontextprotocol.io/specification/2025-03-26/index) — tools are arbitrary execution; consent, access controls, privacy, and untrusted annotations. **Confidence: HIGH** for that revision.
- [MCP client best practices](https://modelcontextprotocol.io/docs/develop/clients/client-best-practices) — progressive discovery and applying confirmation policy to indirect/sandbox-originated calls. **Confidence: HIGH**.
- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — least privilege, agent-specific defenses, and logging. **Confidence: MEDIUM-HIGH** (authoritative community security guidance, not a protocol specification).
- Local project evidence: `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `AGENTS.md`, `.planning/research/FEATURES.md`, and `.planning/research/ARCHITECTURE.md`. **Confidence: HIGH** for local scope, constraints, architecture, and pinned upstream observations.

## Confidence Notes and Gaps

- The upstream repository root and chapter sequence were verified live, while detailed chapter mechanics rely additionally on the existing project research pinned to commit `a9cafe...`; direct raw-file retrieval at that commit was unavailable during this run. This does not weaken the major roadmap warnings, but exact implementation details should be rechecked at chapter start if upstream is repinned.
- Recommendations on atomic file updates, one-writer coordination, and deterministic race testing are engineering safeguards inferred from the demonstrated concurrency model and official library behavior; upstream does not claim production crash safety.
- Real MCP transport is intentionally outside the current milestone. Its version-specific SDK/API details remain an explicit research gap, not an implied feature.
- Feishu API behavior was not researched because this artifact concerns chapter-execution pitfalls, and existing project requirements already define documentation timing. Phase-specific Feishu automation should separately verify permissions, idempotent updates, and secret redaction.

---
*Pitfalls research for: Learn Claude Code by Building*
*Researched: 2026-07-19*
