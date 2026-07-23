# Feishu Sync Rule

Before updating Feishu, ask the user whether the current environment is home or
company.

- Home parent: `https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng`
- Company parent: `https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc`

Do not rely on a single hard-coded parent wiki URL in GSD state. Chapter child
documents are created only after tests, runtime evidence, reflection, commit,
and tag are complete.

## Quality Standard

Feishu child documents are real Feishu online `docx` pages, not raw `.md` Drive
files and not raw dumps of `guide.md`, `reflection.md`, and `evidence.md`.
Before upload, synthesize a polished review document:

- Start with chapter title, status, commit, tag, and a short takeaway.
- Use concise sections with clear headings.
- Keep mechanism explanation readable and not overly long.
- Include only the most important code paths and test/demo evidence.
- Preserve the learner's reflection, but edit it into a smooth review-ready
  paragraph while keeping the original meaning.
- Include commit/tag/Feishu evidence without exposing secrets.
- Prefer tables or short bullets where they improve scanning.

The first s01 upload was an incorrect raw Markdown file. The corrected home
s01 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/WkW6wgMnbifIiTkFuUGcEhYhnWf`

The completed company s02 page is:

- `https://trip.larkenterprise.com/wiki/MwfHwn0Lwi4b9XkWNNUcFUmgnth`

The completed home s02 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/JlozwiR0SizBpWkDHQ9cgyhynFb`

The completed company s03 page is:

- `https://trip.larkenterprise.com/wiki/DqXEw21KWiuzWDkCA6CcYzLAn4g`

The completed home s03 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/Mv0RwNiDmihBRYkYlOockEhjnHh`

The completed home s04 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/PNNRwDIetiz7OjkAdmocdDHenfe`

The completed home s05 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/Dmf6wxoNXimqWbkRT1mcFVEXnid`

The completed home s06 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/KHJUwCe0NiTKmEkLi5IcFUaQnSc`

The completed home s07 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/GGe6wFFePiJEkXk48pGcIHbGnrf`

The completed home s08 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/RhG7wRQlqi4wg8k1D1kcicnvn99`

The completed home s09 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/SidbwRBr8iFc5IkETEZcwZjWnoI`

The completed home s10 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/XKwWwFH6NiB2D9khWBDclbEnnsb`

The completed home s11 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/C8UGwYOBmiTMc7kO4cMcovf4njd`

The completed home s12 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/JlNfwILP9iB7eYkxV1Sciib0nLh`

The completed home s13 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/GnbrwjTpEicMVWkSbhsc0oxxnkR`

The completed home s14 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/CCgYwXtRrifG4HkhGdxcsTqInug`

The completed home s15 page is:

- `https://jcneiirfaiic.feishu.cn/wiki/IantwDzayifprNk0xaVc4e2wnwc`

## Parent Update Safety

Use `lark-cli` for Feishu updates when available. Do not assume
`docs +update --command str_replace` replaces only the first occurrence: it can
replace every matching text fragment in the document. For parent directory
tables, prefer fetching the table block id with `docs +fetch --detail with-ids`
and using `block_replace` for the table, or use patterns that are globally
unique.

The obsolete raw Markdown child is no longer listed under the home parent and
currently resolves as not found:

- `https://jcneiirfaiic.feishu.cn/wiki/K9M4wXtUEiEpb6kv0nzc2d3znrd`
