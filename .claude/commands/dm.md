---
description: Draft cold Twitter/X/LinkedIn DMs in your voice for one or more people
argument-hint: [paste each person's handle + bio / posts / what they build, and what you want]
allowed-tools: Read, Write, Glob
---

The user has pasted info about one or more people to DM, either as
`$ARGUMENTS` or in the message body: handle, bio, posts, what they're
building, how the user knows of them, and (optionally) what the user
wants. Do not fetch any URL or profile — paste-only.

Follow AGENTS.md #14 exactly. Steps:

1. Read every file under `context/` (incl. `profile.md` for closing
   line / links / style rules) and `resume/resume.tex`. These are the
   only allowed sources for facts about the user. Find the voice
   sample(s) — `context/voice*` first, else any file that is clearly the
   user's own casual writing. Study casing, punctuation, sentence
   length, slang, how they open and sign off.
2. Read `dms/*.md` to avoid re-drafting someone already there (same
   handle → ask whether to redraft).
3. For each person, decide the **one ask** (from the paste; if none,
   the lightest reasonable one — usually a specific question about
   their work, not a call or a job).
4. Pick the **hook**: the single most specific thing from the paste and
   the single fact about the user that genuinely connects to it. If
   nothing connects, say so in the file rather than forcing it.
5. Write `dms/<handle>.md` (lowercase, no `@`; collision with a
   different person → suffix `-2`):

   ```
   ---
   handle: "@<handle>"
   name: <name or blank>
   platform: <x | linkedin | other>
   date_drafted: <YYYY-MM-DD>
   ask: <the one ask, few words>
   ---

   ## About them
   <the pasted info, verbatim>

   ## Drafts

   **A** (<angle, 2-4 words>)
   <draft>

   **B** (<angle>)
   <draft>

   **C** (<angle>)   <- optional, only if genuinely different

   ## Follow-up
   <one line, to send once after ~5 days of silence>

   ## Facts used
   - <each claim about the user in the drafts> ← <source file/section>
   ```

   LinkedIn connection notes must fit 300 chars. Drafts are plain text
   (no code fences) so they copy-paste cleanly.
6. Reply with the slug(s), the recommended draft per person (one line
   why), and any `[NEEDS INPUT: ...]` gaps. No voice sample → say so
   once and suggest `/setup voice`.

If the paste is ambiguous (can't tell who's who), ask before writing.
