# email-app/ — send your drafted emails from the terminal (optional)

`/email` (or `python harness.py new email "Name"`) writes drafts to
`emails/<name>-<company>.md`. Copy-pasting them into your mail app works
fine and needs no setup. This folder is a small stdlib-only Python
sender for when you'd rather send from the terminal. **AI tools never
run it with `--send`; sending is always you.**

## 1. Pick your route

| You use | Route | Password needed? |
|---|---|---|
| **Classic Outlook on Windows** (school / work / personal Microsoft account) | `SEND_VIA=outlook` — drives the Outlook app you're already signed into | **No** |
| **Gmail** (personal or Google Workspace) | SMTP + an App Password | 16-char app password |
| **Outlook.com / Microsoft 365, no classic Outlook** (Mac, new Outlook) | SMTP, *if* your account still allows it (many school/work tenants have it off; Microsoft is retiring basic SMTP login) | your password or app password |
| **Anything else** (iCloud, Fastmail, Proton Bridge, Zoho...) | SMTP with your provider's host/port | app password usually |

Then `cp .env.example .env` (it's gitignored) and fill it in **in your
editor**. Never paste a password into an AI chat.

### Classic Outlook (Windows)

1. Make sure you're on **classic** Outlook: the desktop app with a
   **File** menu. "New Outlook" (toggle at top-right) has no automation
   support, so switch the toggle off.
2. In `.env`:
   ```
   SEND_VIA=outlook
   OUTLOOK_ACCOUNT=you@school.edu   # optional; which account to send from if you have several
   ```
3. That's it, no password. The first send may make Outlook show a
   "a program is trying to send email" prompt; click **Allow**.
4. Bonus: `--draft` puts the email in your Outlook **Drafts** folder
   instead of sending, so you can tweak it and hit Send in Outlook.

### Gmail

1. Turn on **2-Step Verification**: myaccount.google.com → Security.
2. Create an **App Password**: myaccount.google.com/apppasswords → name
   it "job-app-harness" → copy the 16 characters. (No such page? 2-Step
   isn't on, or your Workspace admin blocked app passwords; use
   copy-paste instead.)
3. In `.env`:
   ```
   SEND_VIA=smtp
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USER=you@gmail.com
   SMTP_PASSWORD=abcdabcdabcdabcd
   SMTP_FROM=you@gmail.com
   SMTP_FROM_NAME=Your Name
   ```
   Note: SMTP sends don't show in Gmail's Sent folder threading the same
   way; they do appear under Sent.

### Outlook.com / Microsoft 365 over SMTP

`SMTP_HOST=smtp.office365.com` (M365) or `smtp-mail.outlook.com`
(Outlook.com), `SMTP_PORT=587`, user + password (or an app password if
you have 2FA). If login fails with an "authentication unsuccessful /
basic auth disabled" error, your account doesn't allow SMTP. Use the
classic Outlook route on Windows, or copy-paste.

### Other providers

Search "<provider> SMTP settings": you need host, port (465 = SSL,
587 = STARTTLS) and usually an app password.

## 2. Use it

```
python email-app/send.py emails/jane-doe-acme.md                 # dry run: shows exactly what goes out, checks gaps/address/config
python email-app/send.py emails/jane-doe-acme.md --test --send   # send to YOURSELF first
python email-app/send.py emails/jane-doe-acme.md --send          # send for real (type "send" to confirm)
python email-app/send.py emails/jane-doe-acme.md --draft         # Outlook only: drop into Drafts
```

It refuses to send if the draft still has `[NEEDS INPUT: ...]`, the
address looks wrong, or config is missing. After a real send, the
draft's frontmatter becomes `status: sent` + `sent_at:`, a line goes to
`email-app/sent.log` (gitignored), and re-sending is refused.

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

## Troubleshooting

- **Outlook: "Outlook failed ... no COM"**: you're on new Outlook, or
  Outlook isn't installed / signed in. Switch to classic.
- **Outlook: hangs**: a security prompt is waiting behind other
  windows. Click Allow.
- **Gmail: 535 Username and Password not accepted**: you used your
  normal password. Use the App Password.
- **M365: 535 5.7.139 / basic auth disabled**: SMTP is off for your
  tenant. Use classic Outlook or copy-paste.

## Ideas to extend (ask your AI tool to build any of these)

- **Scheduled send**: send at 9am recipient time.
- **Follow-ups**: list `status: sent` drafts older than 5 business days
  and draft the follow-up.
- **Gmail API** (OAuth, proper threading): Google Cloud project → enable
  Gmail API → OAuth desktop client → `credentials.json` (gitignore it).
- **Tracker**: CSV of who you emailed, when, reply status.

Keep the same rules: dry-run default, explicit confirm, secrets only in
gitignored files.
