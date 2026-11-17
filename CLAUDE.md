# CLAUDE.md

Rules for Claude Code operating in this repo. This is a personal
job-application harness: a LaTeX master resume + a context bank, used to
tailor resumes per listing and draft answers, cold DMs, and cold emails.

Layout: personal folders at the root (`resume/`, `context/`, `listings/`,
`output/`, `dms/`, `emails/`) — all gitignored; harness machinery in
`.claude/` (commands, hook, scripts); the optional sender in
`email-app/`; template-only material in `template/`.

Section numbers are stable IDs (not an ordering); commands cite them.

## 1. Privacy (applies to everything)

- Personal data lives only in the gitignored folders above. Never write
  the user's resume, contact info, listings, drafts, or context into a
  tracked file (README, CLAUDE.md, commands, `template/`).
- Before any `git add` / commit, run `git status --short` and confirm no
  personal file is staged. If one is, stop and tell the user.
- New personal folder → add it to `.gitignore` first.
- Never send personal data to an outside service unless the user
  explicitly asks.

## 2. Profile / preferences

- `context/profile.md` (written by `/setup`) holds the user's name,
  links, target roles/terms, sign-off, DM/email closing line, and style
  preferences. Every drafting command reads it. Its preferences override
  the defaults in #10, #14, #15 where they conflict.
- If it doesn't exist, use defaults and suggest running `/setup`.

## 3. Setup / context bank (`/setup`, `/bank`)

- `/setup` onboards a new user by asking, one section at a time: resume,
  profile, context bank (experience + projects), voice sample, common
  Q&A. Skippable and resumable — re-running it fills only what's missing
  unless the user names a section.
- The context bank is `context/bank.md`, built from
  `template/context-bank.md`. One section per job / project with
  **Figures** (numbers + where they come from), **What it is**,
  **Bullets**, **Behavioral evidence** (STAR-ish stories), **Can't
  disclose** (NDA limits). Plus skills inventory, awards, bio, Q&A.
- Interview the user; never fill a field with a guess. Unknown numbers
  get `[NEEDS INPUT: ...]`. Record where each figure came from
  (user said / doc / repo) so later claims stay traceable.
- `/bank` appends or updates one entry later, same rules.

## 9. Guardrails (tailoring)

- Every claim in a tailored resume must trace back to `resume/resume.tex`
  or something in `context/`. No fabrication — no invented metrics,
  titles, dates, or skills.
- You may reorder, reword, drop irrelevant items, or pull in relevant
  items from `context/` that weren't in the base resume. You may not
  invent facts.
- Preserve the base resume's page count.
- Every tailoring run writes `output/<slug>-changes.md` — a plain list of
  what changed and why.

## 10. Application answers

- Draft answers from `resume/` + `context/`. If information needed to
  answer well isn't available, write `[NEEDS INPUT: ...]` inline — never
  block or refuse to draft.
- Under 150 words unless the listing's question specifies a length.
- Match the voice sample in `context/` if one exists; otherwise plain,
  professional, first-person.
- Answers live inside `output/<slug>.tex` as a LaTeX comment block at the
  very top (before `\documentclass`), so they never compile into the
  PDF. Only when the listing has a `## Questions` section. Format, every
  line `%`-prefixed, wrapped ~80 cols:

  ```
  % ==== APPLICATION ANSWERS (comments only; not compiled) ====
  % Q1: <question verbatim>
  % A1: <answer, wrapped, continuation lines start with "%     ">
  %
  % Q2: ...
  % ============================================================
  ```

## 4. Intake (`/intake`)

- Paste-only. Never fetch URLs.
- One file per listing: `listings/<company>-<role>.md`, kebab-case.
- Check `listings/` and `listings/completed/` for slug collisions;
  suffix `-2`, `-3`, etc.
- Frontmatter: `company`, `role`, `url`, `date_added`. Body: verbatim
  paste, then `## Questions` if any survive the filter.
- `## Questions` keeps **only short-answer, application-specific**
  free-text prompts ("why us", "describe a project"). Drop contact
  fields, uploads, work-auth / sponsorship / relocation / EEO, yes-no,
  multiple-choice, dropdown, date, salary, availability. None left →
  omit the section.

## 5. Output (`/process`)

- Flat in `output/`: `<slug>.tex`, `<slug>.pdf`, `<slug>-changes.md`.
  Answers are a comment block inside `<slug>.tex` (#10).
- One subagent per listing, parallel, capped at 4 concurrent.
- After compiling (or giving up, #12), delete build junk: `.aux .log
  .out .fls .fdb_latexmk .synctex.gz`.
- Main session prints a summary table: slug, PDF ok?, gaps count
  (`[NEEDS INPUT: ...]` markers), compile status.

## 6. Completed

- When `/process` generates output, move the listing to
  `listings/completed/`. Folder is the status — no `status:` field.
- Output stays in `output/`. One subfolder level only.

## 12. Compile failure

- On failure: read the `.log`, fix, retry — 3 attempts total.
- Still failing: keep the `.tex`, skip the `.pdf`, report "compile
  failed — open `.tex` in Overleaf".

## 13. Context

- `context/` is freeform (`.md`, `.txt`, `.pdf`, ...). Read all of it
  during `/process`, `/dm`, `/email` — second source of truth alongside
  `resume/resume.tex`.

## 14. Cold DMs (`/dm`)

- Paste-only: never fetch profiles or tweets. Claude only drafts; never
  sends.
- Facts about the user trace to `resume/` or `context/` (#9). Facts
  about the recipient come only from the paste. Unknown →
  `[NEEDS INPUT: ...]`. Every DM file lists claims + sources under
  `## Facts used`.
- Voice: copy `context/voice*` (else the user's own casual writing in
  `context/`) — casing, punctuation, length, slang. No sample → short,
  plain casual voice, and tell the user to add one.
- Shape: ≤60 words (hard cap 80; a "here's something I built" DM may run
  ~110). One ask, easy to say no to. Open with them (a specific thing
  they made/said), not a bio. One fact about the user. At most one link,
  bare (no `https://`), unless `profile.md` sets a standard closing link.
- Avoid (unless the user's own sample uses it): em dashes, "I hope this
  finds you well", "I came across", "I'd love to", "resonated",
  "fascinating", "quick question" opener, "pick your brain", "as a
  [title]...", rule-of-three lists, stacked exclamation marks, flattery
  with no specifics.
- Output: `dms/<handle>.md` — 2-3 drafts, different angles, one
  follow-up line, facts-used list. Format in `.claude/commands/dm.md`.

## 15. Cold emails (`/email`)

- Same sourcing, voice, and avoid-list rules as #14. Paste-only.
- Shape: subject ≤7 words, specific. Body ≤150 words (hard cap 180).
  Lead with the thing relevant to *them*, then one or two lines on the
  user, then one ask. Sign-off + links from `profile.md`. No resume
  attachment unless the user asks.
- Follow up once, ~5 business days later, one or two lines, new info if
  possible. Never email two people at the same company on the same day.
- Output: `emails/<slug>.md` with frontmatter `to`, `subject`, `status:
  draft`, then the body. Exactly one sendable body per file (alternates
  go in a `## Alternates` section below a `---` line the sender ignores).
- Claude never sends email. The optional sender in `email-app/` is run
  by the user, dry-run by default (see `email-app/README.md`). Claude
  may help the user set it up but must not run it with `--send`.

## Hook / compile double-run

`.claude/settings.json` runs `.claude/scripts/compile_hook.py` (via
`python3`, falling back to `python`) as a PostToolUse hook on every
`Write|Edit`, so `.tex` edits in `resume/` or `output/` auto-compile and
clean up after themselves. If `latexmk` isn't on PATH the hook (and
`compile.*` / `watch.*`) probe the usual install dirs first (MiKTeX,
Strawberry Perl, TeX Live, MacTeX). If `latexmk` is still missing or the
compile fails, the hook's message reaches you as additional context:
relay it (incl. the install command) to the user.

`/process` subagents compile explicitly (#12), which would
double-compile against the hook. So `/process` creates the marker
`output/.processing` before launching subagents and deletes it after;
the hook no-ops while the marker exists and is under 2h old. Setting
`JOB_HARNESS_NO_HOOK=1` in the environment Claude Code was launched from
also disables the hook.
