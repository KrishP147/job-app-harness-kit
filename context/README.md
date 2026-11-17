# context/

Your context bank. Claude reads **all** of it for `/process`, `/dm`,
`/email`. `/setup` creates the core files; drop anything else in freely
(`.md`, `.txt`, `.pdf`).

| File | What | Made by |
|---|---|---|
| `profile.md` | name, links, targets, sign-offs, style rules | `/setup profile` |
| `bank.md` | every job/project with figures + sources, stories, skills | `/setup bank`, `/bank` |
| `voice.md` | 10-20 real messages you wrote | `/setup voice` |
| `qa.md` | answers you've already written to common questions | `/setup qa` |
| anything else | old cover letters, write-ups, reviews, transcripts | you |

The more concrete numbers (with where they came from), the better the
output. Nothing is invented: gaps come back as `[NEEDS INPUT: ...]`.

Everything here except this README is gitignored.
