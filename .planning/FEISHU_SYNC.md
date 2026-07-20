# Feishu Sync Rule

Before updating Feishu, ask the user whether the current environment is home or
company.

- Home parent: `https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng`
- Company parent: `https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc`

Do not rely on a single hard-coded parent wiki URL in GSD state. Chapter child
documents are created only after tests, runtime evidence, reflection, commit,
and tag are complete.

## Quality Standard

Feishu child documents are not raw dumps of `guide.md`, `reflection.md`, and
`evidence.md`. Before upload, synthesize a polished review document:

- Start with chapter title, status, commit, tag, and a short takeaway.
- Use concise sections with clear headings.
- Keep mechanism explanation readable and not overly long.
- Include only the most important code paths and test/demo evidence.
- Preserve the learner's reflection, but edit it into a smooth review-ready
  paragraph while keeping the original meaning.
- Include commit/tag/Feishu evidence without exposing secrets.
- Prefer tables or short bullets where they improve scanning.

The current s01 upload was created as a raw Markdown-style file and should be
treated as needing later beautification, not as the target quality bar.
