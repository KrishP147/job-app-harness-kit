---
description: Generate a tailored resume + draft answers for one or all listings
argument-hint: "[slug] (omit to process every listing in listings/)"
allowed-tools: Read, Write, Glob, Bash, Agent
---

Target listings:

- If `$ARGUMENTS` is empty: every `listings/*.md` file at the root of
  `listings/` (not `listings/README.md`, not anything already in
  `listings/completed/`).
- If `$ARGUMENTS` is a slug: find `listings/<slug>.md` first, then
  `listings/completed/<slug>.md` if not found there. Reprocessing an
  already-completed listing is fine — overwrite its `output/` files.

If there are zero target listings, say so and stop. If
`resume/resume.tex` is missing, stop and tell the user to run `/setup`
first. If `context/bank.md` is missing, warn once that output will be
generic and gap-heavy until they run `/setup bank`, then continue.

Before launching subagents, create the marker file `output/.processing`
(e.g. `touch output/.processing`). While it exists the save hook skips
compiling, since subagents compile explicitly. Delete it when all
subagents are done, including on failure.

For each target listing, launch one `Agent` subagent (general-purpose),
running **up to 4 concurrently** (batch launches in groups of 4 if there
are more). Give each subagent this brief, filled in per listing:

> Read `resume/resume.tex` and every file under `context/` (all of it —
> `.md`, `.txt`, `.pdf`). Read the listing at `<path to the listing .md
> file>`. Follow the guardrails and answer rules in the repo's
> `CLAUDE.md` (sections 9, 10, 12) exactly.
>
> Write:
> - `output/<slug>.tex` — the tailored resume. **If** the listing has a
>   `## Questions` section, put drafted answers at the very top of this
>   file as a `%` comment block (format in CLAUDE.md #10) so they stay
>   out of the PDF. Mark anything you can't answer from `resume/` or
>   `context/` with `[NEEDS INPUT: ...]` inline; never block on a gap.
>   No separate answers file.
> - `output/<slug>-changes.md` — what you changed from the base resume
>   and why, plainly stated.
>
> Compile `output/<slug>.tex` yourself (the save hook is paused by
> `output/.processing`), e.g. `bash .claude/scripts/compile.sh
> output/<slug>.tex` (or `.claude/scripts/compile.ps1` from PowerShell —
> both find latexmk even if it isn't on PATH). If it fails,
> read the log, fix the `.tex`, and retry — up to 3 attempts total. If
> still failing after 3 attempts, leave the `.tex` as-is, skip the PDF,
> and report compile failure. Delete LaTeX build junk (`.aux .log .out
> .fls .fdb_latexmk .synctex.gz`) next to the output either way.
>
> Then move the listing file from `listings/` to `listings/completed/`
> (skip this if it was already in `completed/`).
>
> Report back: slug, whether the PDF built, how many `[NEEDS INPUT: ...]`
> gaps you left in the `.tex` comment block, and compile status (ok / failed after retries / latexmk
> not installed).

After all subagents finish, print a summary table:

| slug | pdf ok? | gaps | compile status |
|---|---|---|---|

If `latexmk` isn't installed at all, subagents should still write the
`.tex`, skip compiling, and report that — the table's compile status
column should say so, and you should print the install command once at
the end (see README.md) rather than repeating it per row.
