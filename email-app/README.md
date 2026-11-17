# email-app/ — send your drafted emails from the terminal (optional)

`/email` writes drafts to `emails/<name>-<company>.md`. You can copy-paste
those into Gmail/Outlook by hand — that's the default and needs no setup.
This folder is a ~150-line, stdlib-only Python sender for when you'd
rather send from the terminal. **Claude never runs it with `--send`;
sending is always you.**

## Setup (5 min)

1. **Get SMTP credentials.**
   - **Gmail:** turn on 2-Step Verification, then go to
     Google Account → Security → App passwords, create one named
     "job-app-harness", copy the 16-char password. Host `smtp.gmail.com`,
     port `465`.
   - **Outlook / Microsoft 365:** host `smtp.office365.com`, port `587`
     (your org may require an app password or have SMTP disabled).
   - **Anything else:** your provider's SMTP host/port/user/password.
2. **Create `.env`** at the repo root (it's gitignored):
   `cp .env.example .env`, then fill it in **in your editor**. Don't
   paste the password into the Claude chat.
3. **Dry run** (prints exactly what would go out, checks for
   `[NEEDS INPUT]` gaps, bad addresses, missing config):

   ```
   python email-app/send.py emails/jane-doe-acme.md
   ```
4. **Send a test to yourself:**
   `python email-app/send.py emails/jane-doe-acme.md --test --send`
5. **Send for real:**
   `python email-app/send.py emails/jane-doe-acme.md --send`
   (asks you to type `send`). On success the draft's frontmatter becomes
   `status: sent` + `sent_at:`, and a line goes to `email-app/sent.log`
   (gitignored). Re-sending a `sent` draft is refused.

## Draft format it expects

```
---
to: jane@acme.com
subject: Six words max, specific
status: draft
---

Body that gets sent, plain text.

---
Anything after this line (alternates, follow-up, facts used) is NOT sent.
```

## Want more? Ideas to extend (ask Claude to build any of these)

- **Scheduling:** send at 9am recipient time (`--at`), via a small loop
  or your OS scheduler.
- **Follow-ups:** a `followups.py` that lists `status: sent` drafts older
  than 5 business days with no reply, and drafts the follow-up body.
- **Gmail API instead of SMTP** (OAuth, lands in your Sent folder with
  threading): create a Google Cloud project → enable Gmail API → OAuth
  desktop client → `credentials.json` (gitignore it) → `pip install
  google-api-python-client google-auth-oauthlib`.
- **Tracker:** a CSV of who you emailed, when, reply status.

Keep the same rules: dry-run default, explicit confirm, secrets only in
gitignored files.
