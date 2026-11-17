---
description: Onboard - collect your resume, profile, context bank, voice sample, and common Q&A
argument-hint: "[section] (resume | profile | bank | voice | qa | email-app) - omit to run everything still missing"
allowed-tools: Read, Write, Edit, Glob, Bash
---

You are onboarding the user onto this harness. Follow AGENTS.md #1-#3.
Interview style: ask **one section at a time**, a few questions per
message, plain language. Every section is skippable ("skip" → move on,
note it as TODO at the end). Never invent anything: unknown → leave
`[NEEDS INPUT: ...]`.

First, check what already exists (`resume/resume.tex`,
`context/profile.md`, `context/bank.md`, `context/voice.md`,
`context/qa.md`, `.env`). If `$ARGUMENTS` names a section, run only that
one. Otherwise run every section that's missing, in this order, and
tell the user up front which ones you'll cover (~10-20 min total).

## 1. resume

Ask for their resume. Accept any of:
- a `.tex` file path or pasted LaTeX → save as `resume/resume.tex`
  unchanged;
- a PDF / DOCX / text path or pasted text → convert to LaTeX using the
  structure of `template/examples/resume.tex` (keep every fact, wording,
  date exactly; don't add or embellish), save as `resume/resume.tex`,
  and tell them to eyeball the compiled `resume/resume.pdf`. If they
  have a LaTeX template they prefer (e.g. Jake's Resume on Overleaf),
  ask for it and use it instead.
The save hook compiles it. If latexmk is missing, relay the install
command from README.md.

## 2. profile

Copy `template/profile.md` to `context/profile.md` and fill it by
asking: name as it should appear, email, phone (optional), location,
links (site, GitHub, LinkedIn, X), school/program + grad date (if a
student), target roles + terms/start dates, work authorization notes
they're happy to have mentioned, sign-off for emails, a standard
closing line/link for recruiting DMs (or none), and style rules
(e.g. "all lowercase", "no em dashes", "no colons in DMs").

## 3. bank (context bank)

Copy `template/context-bank.md` to `context/bank.md`. Seed one section
per job / project / activity from the resume, then interview the user
**per entry** (skip entries they don't care about):
- What is it, in one or two sentences a stranger gets?
- What did *you* own vs. the team?
- Numbers: users, latency, money, scale, %, time saved, rank, stars.
  For each, where does it come from (dashboard, repo, estimate)? Mark
  estimates as such.
- Hardest problem and how you solved it.
- One story for behavioral questions (situation → action → result).
- Anything under NDA / not to be disclosed?
Then ask: anything *not* on the resume worth having on file (side
projects, hackathons, leadership, awards, open source)? Add those too.
Also ask them to drop in any existing material (old cover letters,
write-ups, performance reviews, project READMEs, transcripts) — copy
or save those into `context/` as-is; read them and fold facts into the
bank with the file cited as the source.

## 4. voice

Ask for 10-20 real messages they wrote: tweets, DMs, Slack/texts,
emails they're happy with. Paste as-is (they can strip names). Save to
`context/voice.md` using `template/voice.md`'s layout, then write a
2-4 line "voice notes" summary at the top (casing, punctuation, length,
slang, how they open/close) and confirm it with them.

## 5. qa

Ask for answers they've already written to common questions ("why do
you want to work here", "tell me about yourself", "a time you failed",
"conflict", "proudest project", "why this field"). Save to
`context/qa.md`, one `## <question>` per answer, verbatim. Don't
draft new ones here — `/process` does that per listing.

## 6. email-app (optional)

Only if they want to send emails from the terminal. Ask which mail
they use, then walk them through that route in `email-app/README.md`
step by step:
- **Classic Outlook on Windows** → `SEND_VIA=outlook` (+ optional
  `OUTLOOK_ACCOUNT`), no password. Check they're on classic, not new
  Outlook. Mention `--draft` (drops into Outlook Drafts).
- **Gmail** → 2-Step Verification, then App Password, then SMTP vars.
- **Outlook.com / M365 without classic Outlook, or other** → SMTP vars;
  warn that many school/work tenants block SMTP.
Copy `.env.example` → `.env`; they fill secrets **themselves** (never
ask them to paste a password into chat). Then have them run the dry run
and the `--test --send` to themselves, and show you the output. Never
run `--send` (to a real recipient) yourself.

## Finish

Print a short checklist: what's done, what was skipped, files written.
Run `git status --short` and confirm nothing personal shows up as
untracked-and-unignored (if it does, add it to `.gitignore` and say so).
Then suggest next steps: `/intake` a listing → `/process`, `/dm`,
`/email`, `/bank` to add more later.
