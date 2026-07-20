# Coding Workflow From s02 Onward

Starting with s02, the learner will no longer hand-write the chapter code first.
Codex should implement the chapter delta after the guide/discussion step, using
the referenced upstream open-source project only as behavioral reference.

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

1. Codex explains the chapter goal and expected delta.
2. The learner discusses questions and confirms readiness.
3. Codex implements the delta, tests, demo evidence, and chapter records.
4. The learner reviews the PyCharm diff and asks questions.
5. Codex adjusts if needed, then completes tests, commit, tag, push, and Feishu
   archive.

The learner may still edit code manually when desired, but that is no longer the
default workflow after s01.
