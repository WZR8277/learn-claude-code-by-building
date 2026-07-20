# Cross-Computer Learning Sync

This project may be studied from more than one computer. Do not rely on local
Codex chat memory to decide which chapter comes next. Treat the remote Git
repository as the shared source of truth.

GSD-facing summary: `.planning/CROSS_COMPUTER_SYNC.md` contains the short rule
that should be read during project context recovery.

## Source of truth

A chapter is complete only when the remote repository has all of these:

1. One focused chapter commit.
2. One matching tag, such as `s01-agent-loop`.
3. Chapter records under `learning/sXX-short-name/`.

Local Codex memory, IDE state, `.env`, Conda environments, unpushed commits,
and Git stashes are not shared progress.

## Before starting work on either computer

Run this from the repository root:

```bash
git status --short --branch
git fetch --all --tags
git pull --rebase
git tag --list 's*' --sort=v:refname
```

Then inspect the newest chapter tag and continue with the next missing chapter.
For example, if the newest tags are:

```text
s00-init
s01-agent-loop
s02-tool-use
```

start from `s03`, not from whatever the local Codex conversation remembers.

If `git status --short --branch` shows local changes, decide what they are
before pulling:

- Commit finished chapter work.
- Stash or discard temporary experiments only after confirming they are not
  chapter evidence.
- Do not continue chapter work from a dirty tree you do not understand.

## After completing a chapter

Finish the chapter on the same computer with:

```bash
pytest -q
git status --short
git add src tests learning docs README.md pyproject.toml requirements.lock environment.yml
git commit -m "sXX: short chapter name"
git tag sXX-short-name
git push
git push --tags
```

Only push files that belong to the chapter. Never commit `.env`, API keys,
IDE metadata, cache files, or temporary notes.

## Quick prompt for Codex on a second computer

Use this when opening the project on another machine:

```text
Before starting a new chapter, sync Git and tags, inspect the latest sXX-* tag,
read AGENTS.md plus docs/CROSS_COMPUTER_SYNC.md, and tell me which chapter is
safe to continue. Do not rely on local chat memory.
```

## Why this exists

Two computers can have different Codex histories. Git commits and tags are the
only shared, reviewable record of completed chapters, so every session must
check remote tags before choosing the next chapter.
