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
7. The Feishu chapter document records the explanation, reflection, tests, and commit evidence.

