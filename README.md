# job-app-harness

A Claude Code harness for job hunting: tailor your LaTeX resume per
listing, draft application answers, cold DMs, and cold emails — all in
your own voice, from your own facts. Runs locally; your data never
enters git.

> ## ⚠️ Start with `/setup`. It's the whole point.
>
> This harness is only as good as what you give it. Out of the box it
> knows nothing about you, and it **never invents facts** — so with an
> empty context bank you'll get generic output full of
> `[NEEDS INPUT: ...]`.
>
> `/setup` interviews you (~15-20 min, skippable, resumable) and builds
> *your* setup: your resume, your profile and preferences, a context
> bank of your jobs/projects with real numbers, a sample of how you
> actually write, and your existing answers. Every later command reads
> these. **Personalized setup = effective output.** Spend the time
> once; add to it with `/bank` whenever you ship something new.

## Quickstart

Prereqs: [Claude Code](https://docs.claude.com/en/docs/claude-code),
Python 3 (`python3` or `python`). Windows: Git for Windows (Git Bash).

1. **Clone (private copy recommended), `cd` in, run `claude`** from the
   repo root (commands + hook only load there).
2. **Install LaTeX + `latexmk`** (to build PDFs):
   - **Windows:** `winget install MiKTeX.MiKTeX` and
     `winget install StrawberryPerl.StrawberryPerl`
   - **Mac:** `brew install --cask basictex` then `sudo tlmgr install latexmk`
   - **Linux:** `sudo apt install texlive-latex-extra latexmk`

   No TeX? Everything still works; you just get `.tex` (open in Overleaf).
3. **Run `/setup`.** Do this before anything else. Sections:

   | Section | What it asks for | Writes |
   |---|---|---|
   | `resume` | your resume (LaTeX, PDF, DOCX, or pasted text) | `resume/resume.tex` |
   | `profile` | name, links, target roles/terms, sign-offs, style rules | `context/profile.md` |
   | `bank` | per job/project: what it is, your role, numbers + where they're from, hardest problem, a story; plus anything not on the resume; old cover letters/write-ups | `context/bank.md` + files |
   | `voice` | 10-20 real messages you wrote | `context/voice.md` |
   | `qa` | answers you've already written ("why us", "tell me about yourself") | `context/qa.md` |
   | `email-app` | (optional) SMTP setup to send emails from the terminal | `.env` |

   Run one section with `/setup bank` etc. Re-running fills only what's missing.
4. **Use it:**
   - `/intake` → paste a job listing (+ application questions).
   - `/process` → tailored resume PDF + drafted answers per listing.
   - `/dm` → paste someone's handle + bio/posts → 2-3 DMs in your voice.
   - `/email` → paste a recipient + context → cold email draft.
   - `/bank` → add a new project/number/story any time.

Open `output/<slug>.pdf`; `output/<slug>-changes.md` says what changed
and why. Answers sit as a `%` comment block at the top of
`output/<slug>.tex` (never in the PDF). Fill any `[NEEDS INPUT: ...]`
gaps — or better, add the missing fact with `/bank` so it's there next
time.

## Principles

- **No fabrication.** Every claim traces to `resume/` or `context/`.
  Gaps are flagged, never filled with guesses.
- **Your voice.** DMs, emails, and answers copy your voice sample.
- **Specific over generic.** DMs/emails open with the recipient's own
  work, carry one ask, one or two facts about you, no link dumps.
- **Paste-only.** Claude never fetches listings or profiles.
- **Claude drafts, you send.** Nothing is ever sent automatically.
- **Private by default.** All personal folders are gitignored.

## Commands

| Command | Does |
|---|---|
| `/setup [section]` | Onboarding interview → resume, profile, context bank, voice, Q&A |
| `/bank [notes]` | Add/update one context-bank entry |
| `/intake` | Split pasted listing(s) into `listings/<company>-<role>.md` |
| `/process [slug]` | Tailor resume + draft answers; ≤4 listings in parallel; summary table |
| `/dm` | Cold DM drafts → `dms/<handle>.md` |
| `/email` | Cold email drafts → `emails/<name>-<company>.md` |
| `/watch` | Live-recompile `.tex` you edit outside Claude Code |

## Sending email (optional)

`email-app/send.py` sends an `emails/*.md` draft over SMTP (Gmail app
password, Outlook, etc.). Dry-run by default, `--test` sends to
yourself, `--send` asks you to type `send`. Steps in
[`email-app/README.md`](email-app/README.md), or run `/setup email-app`.

## Layout

| Path | What | Tracked? |
|---|---|---|
| `resume/` | master `resume.tex` (+ auto PDF) | no |
| `context/` | profile, bank, voice, Q&A, any docs | no |
| `listings/`, `listings/completed/` | job listings (folder = status) | no |
| `output/` | tailored `.tex` / `.pdf` / `-changes.md` | no |
| `dms/`, `emails/` | drafts | no |
| `.env`, `email-app/sent.log` | SMTP secrets, send log | no |
| `.claude/` | commands, compile hook, scripts | yes |
| `email-app/` | optional sender | yes |
| `template/` | context-bank / profile / voice templates + fictional worked example | yes |
| `CLAUDE.md` | rules Claude follows | yes |

## Privacy

Personal folders keep only a README/`.gitkeep` in git. `.env`, `*.private.*`,
`private/`, and loose `.md`/`.pdf`/`.docx`/`.txt` files at the repo root
are ignored too. Before committing, `git status` should show nothing of
yours. If you fork this publicly, keep your filled-in copy private.
