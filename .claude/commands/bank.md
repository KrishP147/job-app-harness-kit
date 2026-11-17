---
description: Add or update one entry in your context bank (job, project, story, number, Q&A)
argument-hint: "[what to add, e.g. 'new hackathon project' or paste notes / a file path]"
allowed-tools: Read, Write, Edit, Glob
---

Follow AGENTS.md #3. The user wants to add something to
`context/bank.md` (create it from `template/context-bank.md` if
missing). Input is `$ARGUMENTS`, the message body, or a file path.

1. Read `context/bank.md` and decide: new section, or update to an
   existing one (match by name). Updating → show what you'll change.
2. Extract what the paste/file already says. For missing fields of
   that section (What it is, your role, Figures + source, hardest
   problem, a behavioral story, can't-disclose), ask the user — a few
   questions in one message, skippable. Never guess numbers.
3. Write it in the template's format. Every figure gets a source tag
   (`[user]`, `[doc: <file>]`, `[repo]`, `[estimate]`).
4. If they gave a file, also save a copy into `context/` (if not
   already there).
5. Reply with a 2-3 line summary of what was added and any
   `[NEEDS INPUT: ...]` left.
