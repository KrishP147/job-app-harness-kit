---
description: Split pasted job listing(s) into listings/<company>-<role>.md
argument-hint: [paste one or more job listings after the command, or paste in the next message]
allowed-tools: Read, Write, Glob, Bash(git status:*)
---

The user has pasted one or more job listings (and possibly application
questions) either as `$ARGUMENTS` or in the message body. Do not fetch any
URL — listing text is paste-only.

For each distinct listing:

1. Identify `company`, `role`, and `url` (if a URL was pasted; leave blank
   if not given). Use today's date for `date_added`.
2. Derive a slug: kebab-case `<company>-<role>` (lowercase, spaces and
   punctuation to hyphens, no double hyphens).
3. Check for a collision against **both** `listings/*.md` and
   `listings/completed/*.md`. If the slug is already taken, suffix `-2`,
   `-3`, etc. until it's free.
4. Write `listings/<slug>.md`:

   ```
   ---
   company: <company>
   role: <role>
   url: <url or blank>
   date_added: <YYYY-MM-DD>
   ---

   <verbatim pasted listing text>

   ## Questions

   <application questions that survive the filter below, one per numbered
   line, verbatim — omit this section entirely if none survive>
   ```

   **Question filter** (AGENTS.md #4): keep only short-answer,
   application-specific questions — free-text prompts about the
   candidate, the role, or the company ("why us", "describe a time you…",
   "what interests you about…"). Drop everything else even though it was
   pasted: name / email / phone / address / links, resume or cover-letter
   uploads, work authorization, sponsorship, relocation, EEO /
   demographic / veteran / disability, yes-no, multiple choice, checkbox,
   dropdown, dates, salary, availability, "how did you hear about us".

5. Confirm to the user what file(s) were written, with their slugs.

If the paste is ambiguous (can't tell company/role, or can't tell where
one listing ends and the next begins), ask before writing files rather
than guessing.
