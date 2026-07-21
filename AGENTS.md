# Project Instructions

## Purpose

This repository is a chapter-by-chapter reconstruction of the core harness mechanisms taught by `shareAI-lab/learn-claude-code`.

## Learning workflow

- Keep one evolving implementation under `src/mini_claude_code/`.
- Each chapter introduces only the mechanism taught in that chapter.
- Complete the chapter notes, reflection, tests, and runtime evidence before committing.
- Use exactly one learning commit for each chapter and tag it as `sXX-short-name`.
- Do not copy the upstream implementation verbatim; understand it, then implement and explain it independently.
- Never commit secrets, API keys, access tokens, or `.env`.

## Cross-computer and GSD workflow

- Before starting or closing any chapter, fetch remote tags and use the newest remote `sXX-*` tag as the source of truth for completed chapters.
- Read `.planning/STATE.md`, `.planning/PROJECT.md`, `.planning/CROSS_COMPUTER_SYNC.md`, `.planning/FEISHU_SYNC.md`, and `.planning/CODING_WORKFLOW.md` when restoring context.
- From `s02` onward, Codex first gives a concise chapter guide and diff-review pointers, then implements the uncommitted chapter delta without requiring the learner to preselect discussion topics or confirm readiness. The learner reviews the PyCharm diff, asks questions, and confirms before final commit/tag/archive.
- Code written by Codex should keep methods clear, module/file splits reasonable, and Chinese comments focused on important Agent harness concepts.
- Before updating Feishu, ask whether the user is at home or company, then choose the matching parent wiki from `.planning/FEISHU_SYNC.md`.
- Feishu chapter documents must be polished for review: visually clean, concise, well-structured, and easy to revisit. Do not upload a raw concatenation of local Markdown notes as the final chapter document.

## Skill restrictions

- This is an Agent-related learning project. Do not invoke or rely on any skill whose name starts with `trn-`.
- General-purpose skills such as `grill-me` and GSD-style skills remain allowed when otherwise applicable.
- This restriction applies to every agent and subagent working in this repository.

## Definition of done for a chapter

1. The chapter goal and delta from the previous chapter are documented.
2. The new mechanism is implemented in the evolving codebase.
3. Automated tests pass.
4. A safe, reproducible runtime demonstration is recorded.
5. The learner's personal reflection is captured.
6. The chapter has one focused commit and one matching tag.
7. The Feishu chapter document records the explanation, reflection, tests, and commit evidence in a clean, concise, visually readable format.
