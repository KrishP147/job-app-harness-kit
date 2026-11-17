---
description: Draft cold emails (recruiters, founders, engineers, alumni) in your voice
argument-hint: [paste recipient name + email + who they are / what they work on, and what you want]
allowed-tools: Read, Write, Glob
---

The user pasted info about one or more email recipients (`$ARGUMENTS`
or message body): name, address, role/company, what they work on,
any shared connection, and the ask. Paste-only — never fetch URLs.

Follow CLAUDE.md #15 (and #14's sourcing/voice/avoid rules). Steps:

1. Read all of `context/` (esp. `profile.md` for sign-off, links,
   style) and `resume/resume.tex`. Read `listings/` + `listings/completed/`
   for a matching role at their company (cite it if relevant).
2. Read `emails/*.md`: same recipient → ask before redrafting; another
   person at the same company → warn about same-day sends.
3. Decide the one ask and the hook (most specific thing about *them* +
   the one or two facts about the user that connect).
4. Write `emails/<firstname-lastname>-<company>.md` (kebab-case;
   collision → `-2`):

   ```
   ---
   to: <address, or [NEEDS INPUT: email]>
   name: <recipient name>
   company: <company>
   subject: <≤7 words>
   status: draft
   date_drafted: <YYYY-MM-DD>
   ---

   <the one sendable body, plain text, ending with sign-off from profile.md>

   ---

   ## Alternates
   **B** (<angle>) — subject: <...>
   <body>

   ## Follow-up
   <1-2 lines, send once after ~5 business days>

   ## About them
   <pasted info, verbatim>

   ## Facts used
   - <claim about the user> ← <source file/section>
   ```

   Everything after the first `---` line following the body is ignored
   by the sender; only the top body is sent.
5. Reply: file(s), subject + one-line why for the main draft, any
   `[NEEDS INPUT: ...]`. If the user has set up `email-app/`, remind
   them of the dry-run command
   (`python email-app/send.py emails/<file>.md`). Never run it with
   `--send` — sending is the user's action.
