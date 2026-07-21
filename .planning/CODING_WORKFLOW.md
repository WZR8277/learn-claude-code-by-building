# Coding Workflow From s02 Onward

Starting with s02, the learner will no longer hand-write the chapter code first.
Codex should give a concise chapter guide and diff-review pointers, then
implement the chapter delta using the referenced upstream open-source project
only as behavioral reference. On this computer, read the local upstream checkout
first:

- `/Users/loganlee/Desktop/Pyprojs/learn-claude-code-main`

Use network access for upstream code only when the local checkout is missing,
out of date for the requested task, or the learner explicitly asks to verify
remote content. Pre-implementation discussion is optional, not a
gate, and the learner is not required to predict or select discussion topics
before seeing the code.

## Implementation Rules

- Preserve the single evolving implementation under `src/mini_claude_code/`.
- Before coding, compare the current upstream chapter with its predecessor and
  identify the exact runtime behavior added by the current chapter.
- Prefer the local upstream checkout when comparing chapters. For example,
  compare `../learn-claude-code-main/s04_hooks/` with
  `../learn-claude-code-main/s03_permission/` from this repository's current
  home-computer location. On another computer, find that machine's local
  `learn-claude-code-main` path instead of assuming this absolute path exists.
- Treat that upstream runtime behavior as the chapter ceiling. Implement only
  the current chapter delta.
- Do not copy upstream code verbatim. Re-express the understood mechanism in the
  evolving local structure without redesigning or expanding its feature set.
- Keep methods small, clear, and reasonably named.
- Keep module/file boundaries intentional. Upstream may use one `code.py` per
  chapter; this project may split equivalent behavior across modules, but must
  not keep parallel chapter source copies or introduce extra runtime behavior.
- Deterministic test seams are allowed only when they preserve production
  behavior, stay minimal, and do not introduce a mechanism from a later
  chapter. Tests should patch the current seam rather than require a legacy
  production API.
- When a chapter intentionally evolves an internal interface, update earlier
  tests to exercise the current interface. Do not preserve obsolete parameters,
  compatibility branches, fallback behavior, or duplicate execution paths in
  production code solely for old tests.
- Add clear Chinese comments where they help explain Agent harness concepts or
  non-obvious control flow. Do not add noisy comments for obvious assignments.
- Match the existing code style while staying inside the chapter's behavioral
  ceiling.
- Do not add validation, safeguards, error normalization, concurrency,
  abstractions, or future roadmap features merely because they seem cleaner or
  safer. If upstream does not teach them in the current chapter, obtain the
  learner's explicit approval first.
- Treat `.planning/research/` as background rather than an implementation
  specification. If it conflicts with the learner's current decision,
  `AGENTS.md`, or the current upstream chapter, those sources take precedence.

## Review Rhythm

1. Codex briefly explains the chapter goal, expected delta, and useful points to
   watch while reviewing the diff.
2. Codex implements the delta, tests, and reproducible demo evidence, leaving
   the chapter changes uncommitted for review.
3. The learner reviews the PyCharm diff, asks questions based on the actual
   code, records personal observations, and requests adjustments if needed.
4. Codex explains and adjusts the implementation until the learner confirms it.
5. Codex finalizes chapter records and verification, then creates the single
   chapter commit, tag, push, and polished Feishu archive.

The pre-implementation guide may include attention points or prompts for
reflection, but it must not force the learner to choose discussion areas before
the diff exists.

The learner may still edit code manually when desired, but that is no longer the
default workflow after s01.
