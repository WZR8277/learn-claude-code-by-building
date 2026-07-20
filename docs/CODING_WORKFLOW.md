# Coding Workflow From s02 Onward

Starting with s02, Codex writes the chapter implementation after the learning
discussion. The learner reviews the PyCharm diff, asks questions, and approves
the chapter direction before final commit/tag/archive.

Code expectations:

- Use the upstream open-source chapter as behavioral reference, not as code to
  copy verbatim.
- Keep file splits and method boundaries clear.
- Preserve one evolving implementation in `src/mini_claude_code/`.
- Add focused tests for the new mechanism and regression coverage for previous
  behavior.
- Use clear Chinese comments for important Agent harness concepts and
  non-obvious control flow.
- Avoid early implementation of future chapters.

The GSD-facing version of this rule lives in `.planning/CODING_WORKFLOW.md`.
