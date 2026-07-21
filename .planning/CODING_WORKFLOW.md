# Coding Workflow From s02 Onward

Starting with s02, the learner will no longer hand-write the chapter code first.
Codex should give a concise chapter guide and diff-review pointers, then
implement the chapter delta using the referenced upstream open-source project
only as behavioral reference. Pre-implementation discussion is optional, not a
gate, and the learner is not required to predict or select discussion topics
before seeing the code.

## Implementation Rules

- Preserve the single evolving implementation under `src/mini_claude_code/`.
- Do not copy upstream code verbatim.
- Implement only the current chapter delta.
- Keep methods small, clear, and reasonably named.
- Keep module/file boundaries intentional; split code when it clarifies the
  mechanism or prepares the current chapter boundary.
- Prefer deterministic, injectable seams for model, filesystem, command, and
  clock behavior.
- Add clear Chinese comments where they help explain Agent harness concepts or
  non-obvious control flow. Do not add noisy comments for obvious assignments.
- Match the existing code style unless it conflicts with clarity or safety.

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
