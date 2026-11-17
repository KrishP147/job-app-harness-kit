#!/usr/bin/env python3
"""Send a drafted email from emails/<file>.md over SMTP.

Dry-run by default (prints exactly what would be sent). Add --send to
actually send; you'll be asked to type "send" to confirm. Stdlib only.

Config comes from .env at the repo root (see .env.example).
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
    ap.add_argument("--test", action="store_true", help="send to yourself (SMTP_FROM) instead of the recipient")
    args = ap.parse_args()

    env = {**load_env(ROOT / ".env"), **{k: v for k, v in os.environ.items() if k.startswith("SMTP_")}}
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
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"):
        if not env.get(key):
            problems.append(f"{key} missing from .env")

    sender = env.get("SMTP_FROM", "")
    rcpt = sender if args.test else to
    msg = EmailMessage()
    msg["From"] = formataddr((env.get("SMTP_FROM_NAME", ""), sender)) if sender else ""
    msg["To"] = rcpt
    msg["Subject"] = ("[TEST] " if args.test else "") + subject
    msg["Message-ID"] = make_msgid()
    msg.set_content(body)

    print("=" * 60)
    print(f"From:    {msg['From']}")
    print(f"To:      {rcpt}" + ("   (TEST: real recipient " + to + ")" if args.test else ""))
    print(f"Subject: {msg['Subject']}")
    print("-" * 60)
    print(body)
    print("=" * 60)
    if problems:
        print("NOT SENDABLE:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    if not args.send:
        print("dry run - nothing sent. Add --test to send to yourself, --send to send for real.")
        return

    if input(f"Type 'send' to email {rcpt}: ").strip() != "send":
        sys.exit("aborted, nothing sent")

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

    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{rcpt}\t{msg['Subject']}\t{args.draft}\n")
    if not args.test:
        mark_sent(args.draft, lines, end)
    print(f"sent to {rcpt}")


if __name__ == "__main__":
    main()
