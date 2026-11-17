# job-app-harness

An AI harness for job hunting (Claude Code, Codex, Cursor, Gemini, Copilot, any chat website, or no AI): tailor your LaTeX resume per
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

## Which AI do I need? (any, or none)

Pick whichever you have. Same rules, same files, same output.

| You have | How you use it |
|---|---|
| **Claude Code** (best: auto-compile hook, parallel `/process`) | run `claude` in the repo, type `/setup`, `/process`, ... |
| **Codex CLI, Cursor, Gemini CLI, GitHub Copilot (VS Code), Aider** | open the repo in it. They all read `AGENTS.md` (the rules). Cursor / Gemini / Copilot also get the same `/setup`, `/process`, ... commands (shims in `.cursor/`, `.gemini/`, `.github/prompts/`). In Codex or Aider, just say "run setup", "run process", etc. |
| **Only a chat website** (ChatGPT, Gemini, Claude.ai, ...) | `python harness.py prompt setup` builds one prompt with all the rules + your files, copies it to your clipboard. Paste it into the chat, save the reply to `reply.txt`, run `python harness.py apply reply.txt` (writes the files, builds the PDF). Works for `setup`, `process <slug>`, `dm`, `email`, `bank`. |
| **No AI at all** | `python harness.py new tailor <slug>` (copies your resume + answer stubs + a tailoring checklist), `new email "Jane Doe"`, `new dm @handle` (templates with the rules inline), then `compile`, and send with `email-app/`. You do the writing; the harness keeps it organized and private. |

Run `python harness.py` for all commands (stdlib Python, no installs).
`python harness.py status` shows what you have and how many
`[NEEDS INPUT]` gaps are left; `python harness.py check` confirms
nothing personal is about to be committed.

## Getting your own copy

Your data never gets committed: every personal folder is gitignored,
so even a public fork would carry only the harness. Still, keep your
copy **private** (it's easy to slip a file into the wrong place):

- **On GitHub:** click **Use this template → Create a new repository →
  Private**, then clone it. (Better than forking: forks of a public
  repo can't be made private.)
- **Local only:** `git clone <this repo>` and never push. Fine too —
  your files only ever live on your machine.

Pulling harness updates later: `git remote add upstream <this repo>`,
then `git pull upstream main`. Your personal files are untouched
since git doesn't track them.

## Quickstart

Prereqs: an AI tool from the table above (or none), Python 3 (`python3` or `python`).
Windows: Git for Windows (Git Bash).

1. **Get your copy (above), `cd` in, open your AI tool there** (e.g.
   `claude`; commands only load from the repo root). It will ask permission
   the first time it writes files or runs the compile script — approve
   them (or pick "don't ask again" for this repo).
2. **Install LaTeX + `latexmk`** (to build PDFs):
   - **Windows:** `winget install MiKTeX.MiKTeX` and
     `winget install StrawberryPerl.StrawberryPerl`
   - **Mac:** `brew install --cask basictex` then `sudo tlmgr install latexmk`
   - **Linux:** `sudo apt install texlive-latex-extra latexmk`

   No TeX? Everything still works; you just get `.tex` (open in Overleaf).
3. **Run `/setup`** (chat website: `python harness.py prompt setup`).
   Do this before anything else. Sections:

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

`email-app/send.py` sends an `emails/*.md` draft through **classic
Outlook on Windows** (no password, uses the app you're signed into, can
also drop drafts into Outlook's Drafts), **Gmail** (App Password), or any
**SMTP** provider. Dry run by default, `--test --send` sends to yourself,
`--send` asks you to type `send`. Step-by-step per provider in
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
| `AGENTS.md` | the rules every AI follows (`CLAUDE.md` just imports it) | yes |
| `harness.py` | CLI for chat-website and no-AI use | yes |
| `.cursor/` `.gemini/` `.github/prompts/` `.aider.conf.yml` | command shims for other tools (`python harness.py sync` regenerates) | yes |

## Privacy

Personal folders keep only a README/`.gitkeep` in git. `.env`, `*.private.*`,
`private/`, and loose `.md`/`.pdf`/`.docx`/`.txt` files at the repo root
are ignored too. Before committing, `git status` should show nothing of
yours. If you fork this publicly, keep your filled-in copy private.
