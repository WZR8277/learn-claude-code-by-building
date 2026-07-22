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

The Feishu child document must be a polished Feishu online `docx` page, not a
raw `.md` Drive file or a concatenation of local Markdown files. Keep it
visually clean, concise, and easy to revisit:

- title, status, commit, tag, and one short takeaway near the top
- clear sections for mechanism, code paths, tests/demo, reflection, and evidence
- short bullets or tables for scanability
- no secrets, raw keys, or noisy terminal dumps

The corrected home s01 page is
`https://jcneiirfaiic.feishu.cn/wiki/WkW6wgMnbifIiTkFuUGcEhYhnWf`. The obsolete
raw Markdown child
`https://jcneiirfaiic.feishu.cn/wiki/K9M4wXtUEiEpb6kv0nzc2d3znrd` is no longer
listed under the home parent and currently resolves as not found.

Current known home chapter pages:

- s01: `https://jcneiirfaiic.feishu.cn/wiki/WkW6wgMnbifIiTkFuUGcEhYhnWf`
- s02: `https://jcneiirfaiic.feishu.cn/wiki/JlozwiR0SizBpWkDHQ9cgyhynFb`
- s03: `https://jcneiirfaiic.feishu.cn/wiki/Mv0RwNiDmihBRYkYlOockEhjnHh`
- s04: `https://jcneiirfaiic.feishu.cn/wiki/PNNRwDIetiz7OjkAdmocdDHenfe`
- s05: `https://jcneiirfaiic.feishu.cn/wiki/Dmf6wxoNXimqWbkRT1mcFVEXnid`
- s06: `https://jcneiirfaiic.feishu.cn/wiki/KHJUwCe0NiTKmEkLi5IcFUaQnSc`
- s07: `https://jcneiirfaiic.feishu.cn/wiki/GGe6wFFePiJEkXk48pGcIHbGnrf`
- s08: `https://jcneiirfaiic.feishu.cn/wiki/RhG7wRQlqi4wg8k1D1kcicnvn99`
- s09: `https://jcneiirfaiic.feishu.cn/wiki/SidbwRBr8iFc5IkETEZcwZjWnoI`
- s10: `https://jcneiirfaiic.feishu.cn/wiki/XKwWwFH6NiB2D9khWBDclbEnnsb`
- s11: `https://jcneiirfaiic.feishu.cn/wiki/C8UGwYOBmiTMc7kO4cMcovf4njd`
- s12: `https://jcneiirfaiic.feishu.cn/wiki/JlNfwILP9iB7eYkxV1Sciib0nLh`

## Parent Update Safety

Use `lark-cli` for Feishu updates when available. `docs +update --command
str_replace` can replace every matching text fragment, not just the first one.
For parent directory tables, prefer fetching the table block id and using
`block_replace`, or use patterns that are globally unique.
