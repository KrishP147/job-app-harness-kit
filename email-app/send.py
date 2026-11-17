#!/usr/bin/env python3
"""Send a drafted email from emails/<file>.md (SMTP, or classic Outlook on Windows).

Dry-run by default (prints exactly what would be sent). Add --send to
actually send; you'll be asked to type "send" to confirm. Stdlib only.

Config comes from .env at the repo root (see .env.example).
SEND_VIA=outlook uses classic Outlook (Windows) - no password needed;
--draft puts the email in your Outlook Drafts instead of sending.
"""
import argparse
import datetime as dt
import os
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = Path(__file__).resolve().parent / "sent.log"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def parse_draft(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        sys.exit(f"{path}: missing frontmatter (first line must be ---)")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        sys.exit(f"{path}: frontmatter never closed")
    meta = {}
    for line in lines[1:end]:
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    body = []
    for line in lines[end + 1:]:
        if line.strip() == "---":  # everything after = alternates/notes
            break
        body.append(line)
    return meta, "\n".join(body).strip() + "\n", lines, end


def mark_sent(path: Path, lines, end):
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    fm = lines[1:end]
    fm = [l for l in fm if not l.startswith("status:") and not l.startswith("sent_at:")]
    fm += ["status: sent", f"sent_at: {stamp}"]
    path.write_text("\n".join(["---", *fm, *lines[end:]]) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("draft", type=Path, help="emails/<file>.md")
    ap.add_argument("--send", action="store_true", help="actually send (asks to confirm)")
    ap.add_argument("--test", action="store_true", help="send to yourself instead of the recipient")
    ap.add_argument("--draft", dest="to_drafts", action="store_true",
                    help="Outlook only: put it in your Outlook Drafts folder instead of sending")
    args = ap.parse_args()

    env = {**load_env(ROOT / ".env"),
           **{k: v for k, v in os.environ.items() if k.startswith(("SMTP_", "OUTLOOK_", "SEND_VIA"))}}
    via = env.get("SEND_VIA", "smtp").lower()
    if via not in ("smtp", "outlook"):
        sys.exit(f"SEND_VIA must be smtp or outlook, not {via!r}")
    meta, body, lines, end = parse_draft(args.draft)

    to = meta.get("to", "")
    subject = meta.get("subject", "")
    problems = []
    if "[NEEDS INPUT" in body or "[NEEDS INPUT" in to or "[NEEDS INPUT" in subject:
        problems.append("draft still has [NEEDS INPUT: ...] gaps")
    if not EMAIL_RE.match(to):
        problems.append(f"'to' is not a valid address: {to!r}")
    if not subject:
        problems.append("no subject")
    if meta.get("status") == "sent":
        problems.append(f"already sent ({meta.get('sent_at', '?')}); set status: draft to resend")
    if via == "smtp":
        for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"):
            if not env.get(key):
                problems.append(f"{key} missing from .env")
        if args.to_drafts:
            problems.append("--draft only works with SEND_VIA=outlook")
    elif sys.platform != "win32":
        problems.append("SEND_VIA=outlook needs Windows + classic Outlook (use smtp on Mac/Linux)")

    if via == "outlook":
        sender = env.get("OUTLOOK_ACCOUNT", "") or "(your default Outlook account)"
    else:
        sender = formataddr((env.get("SMTP_FROM_NAME", ""), env.get("SMTP_FROM", ""))) if env.get("SMTP_FROM") else ""
    rcpt = "(yourself)" if args.test else to
    subj = ("[TEST] " if args.test else "") + subject

    print("=" * 60)
    print(f"Via:     {via}" + ("  -> Outlook Drafts (not sent)" if args.to_drafts else ""))
    print(f"From:    {sender}")
    print(f"To:      {rcpt}" + ("   (TEST: real recipient " + to + ")" if args.test else ""))
    print(f"Subject: {subj}")
    print("-" * 60)
    print(body)
    print("=" * 60)
    if problems:
        print("NOT SENDABLE:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    if not (args.send or args.to_drafts):
        print("dry run - nothing sent. --test --send = send to yourself, --send = send for real"
              + (", --draft = save to Outlook Drafts." if via == "outlook" else "."))
        return

    if args.to_drafts:
        rcpt = outlook(env, to, subj, body, mode="draft", test=args.test)
        print(f"saved to Outlook Drafts (to {rcpt}). Review and send it from Outlook.")
        return

    if input(f"Type 'send' to email {rcpt}: ").strip() != "send":
        sys.exit("aborted, nothing sent")

    if via == "outlook":
        rcpt = outlook(env, to, subj, body, mode="send", test=args.test)
    else:
        rcpt = env["SMTP_FROM"] if args.test else to
        smtp_send(env, rcpt, subj, body)

    with LOG.open("a", encoding="utf-8") as f:
        f.write("\t".join([dt.datetime.now().isoformat(timespec="seconds"), via, rcpt, subj, str(args.draft)]) + "\n")
    if not args.test:
        mark_sent(args.draft, lines, end)
    print(f"sent to {rcpt} via {via}")


def smtp_send(env, rcpt, subject, body):
    msg = EmailMessage()
    msg["From"] = formataddr((env.get("SMTP_FROM_NAME", ""), env["SMTP_FROM"]))
    msg["To"] = rcpt
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid()
    msg.set_content(body)
    port = int(env["SMTP_PORT"])
    ctx = ssl.create_default_context()
    if port == 465:
        server = smtplib.SMTP_SSL(env["SMTP_HOST"], port, context=ctx)
    else:
        server = smtplib.SMTP(env["SMTP_HOST"], port)
        server.starttls(context=ctx)
    with server:
        server.login(env["SMTP_USER"], env["SMTP_PASSWORD"])
        server.send_message(msg)


# Classic Outlook via COM, driven through PowerShell (no pip installs).
# Values travel in env vars, never spliced into the script, so quotes in a
# subject/body can't break or inject anything.
OUTLOOK_PS = r"""
$ErrorActionPreference = 'Stop'
$o = New-Object -ComObject Outlook.Application
$accts = @($o.Session.Accounts)
if ($env:JH_ACCOUNT) {
  $a = $accts | Where-Object { $_.SmtpAddress -eq $env:JH_ACCOUNT } | Select-Object -First 1
  if (-not $a) { throw "No Outlook account $($env:JH_ACCOUNT). Have: $(($accts | % SmtpAddress) -join ', ')" }
} else { $a = $accts[0] }
$m = $o.CreateItem(0)
$m.To = if ($env:JH_TEST -eq '1') { $a.SmtpAddress } else { $env:JH_TO }
$m.Subject = $env:JH_SUBJECT
$m.Body = $env:JH_BODY
$m.SendUsingAccount = $a
if ($env:JH_MODE -eq 'draft') { $m.Save() } else { $m.Send() }
Write-Output $m.To
"""


def outlook(env, to, subject, body, mode, test):
    import subprocess
    penv = {**os.environ, "JH_TO": to, "JH_SUBJECT": subject, "JH_BODY": body.replace("\n", "\r\n"),
            "JH_ACCOUNT": env.get("OUTLOOK_ACCOUNT", ""), "JH_MODE": mode, "JH_TEST": "1" if test else "0"}
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", OUTLOOK_PS],
                       env=penv, capture_output=True, text=True, timeout=120)
    if r.returncode:
        sys.exit("Outlook failed (is classic Outlook installed and signed in? new Outlook has no COM):\n"
                 + r.stderr.strip()[-800:])
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else to


if __name__ == "__main__":
    main()
