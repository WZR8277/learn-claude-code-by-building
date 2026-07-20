# Cross-Computer Sync Rule

This project is studied from multiple computers. GSD and Codex must not use
local chat memory as the source of truth for chapter progress.

Before planning or starting any chapter:

```bash
git status --short --branch
git fetch --all --tags
git pull --rebase
git tag --list 's*' --sort=v:refname
```

The latest remote `sXX-*` tag determines the newest completed chapter. Continue
from the next missing chapter.

A chapter is complete only when the remote repository has:

1. One focused chapter commit.
2. One matching `sXX-*` tag.
3. Chapter records under `learning/sXX-short-name/`.

See `docs/CROSS_COMPUTER_SYNC.md` for the full human handoff workflow.
