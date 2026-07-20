# Feishu Sync

This project uses different Feishu parent wiki documents on different
computers. Before creating or updating a chapter document, ask the user:

```text
现在是在家还是在公司？
```

Use the answer to choose the parent wiki:

| Environment | Parent wiki |
|-------------|-------------|
| Home | https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng |
| Company | https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc |

Never assume the parent from local Codex memory. The chapter content should be
created only after code, tests, runtime evidence, learner reflection, commit,
and tag are complete.

## Document Quality

The Feishu child document must be a polished review artifact, not a raw
concatenation of local Markdown files. Keep it visually clean, concise, and easy
to revisit:

- title, status, commit, tag, and one short takeaway near the top
- clear sections for mechanism, code paths, tests/demo, reflection, and evidence
- short bullets or tables for scanability
- no secrets, raw keys, or noisy terminal dumps

The first s01 upload is known to be below this target quality and should be
beautified later.
