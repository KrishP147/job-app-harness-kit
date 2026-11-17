#!/usr/bin/env python3
"""job-app-harness CLI: works with any AI chat, or no AI at all. Stdlib only.

  python harness.py status                      what you have, gaps left
  python harness.py intake [file]               save a pasted listing to listings/
  python harness.py prompt <task> [target]      build a copy-paste prompt for ANY chatbot
        tasks: setup | process <slug> | dm | email | bank
  python harness.py apply [file]                write the chatbot's === FILE === reply into the repo
  python harness.py new <kind> <name>           no-AI templates: tailor <slug> | email <name> | dm <handle>
  python harness.py compile [file.tex]          build a PDF (default resume/resume.tex)
  python harness.py check                       make sure nothing personal is about to be committed
  python harness.py sync                        regenerate command shims for Gemini/Cursor/Copilot

Without [file], intake/apply read stdin: paste, then Ctrl-D (Mac/Linux)
or Ctrl-Z + Enter (Windows).
"""
import datetime as dt
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CMDS = ROOT / ".claude" / "commands"
PERSONAL = ["resume", "context", "listings", "output", "dms", "emails"]
WRITABLE = ["resume", "context", "output", "dms", "emails", "listings"]
TEXT_EXT = {".md", ".txt", ".tex", ".csv", ".json"}
TODAY = dt.date.today().isoformat()
FILE_RE = re.compile(r"^=== FILE: (.+?) ===\s*$\n(.*?)^=== END FILE ===\s*$", re.M | re.S)

TASK_ASK = {
    "setup": "Interview me now, starting with section 1.",
    "dm": "The people I want to DM (handle, bio, posts, what I want):\n\n<PASTE HERE>",
    "email": "The people I want to email (name, address, role, what they work on, what I want):\n\n<PASTE HERE>",
    "bank": "What I want to add to my context bank:\n\n<PASTE HERE>",
}

FILE_PROTOCOL = """\
## How to give me files (IMPORTANT)
You can't write to my disk. Whenever the instructions say to write a
file, put its full contents in your reply exactly like this (one block
per file, path relative to the repo root, no code fences around it):

=== FILE: path/to/file.md ===
<entire file contents>
=== END FILE ===

I'll run `python harness.py apply` to save them. Ignore instructions
about running shell commands, compiling, moving files, or spawning
subagents: I'll do those. If you need something you don't have (a file,
an answer), ask me.
"""


# ---------- helpers ----------

def die(msg):
    sys.exit(f"error: {msg}")


def read_in(path):
    if path:
        return Path(path).read_text(encoding="utf-8")
    print("Paste now, then Ctrl-D (Mac/Linux) or Ctrl-Z + Enter (Windows):", file=sys.stderr)
    return sys.stdin.read()


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def slugify(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def free_slug(base):
    slug, n = base, 2
    while (ROOT / "listings" / f"{slug}.md").exists() or (ROOT / "listings" / "completed" / f"{slug}.md").exists():
        slug, n = f"{base}-{n}", n + 1
    return slug


def find_listing(slug):
    for p in (ROOT / "listings" / f"{slug}.md", ROOT / "listings" / "completed" / f"{slug}.md"):
        if p.exists():
            return p
    die(f"no listing '{slug}' in listings/ or listings/completed/")


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def hook_module():
    spec = importlib.util.spec_from_file_location("compile_hook", ROOT / ".claude" / "scripts" / "compile_hook.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def copy_clipboard(text):
    for cmd in (["clip"], ["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"]):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, input=text.encode("utf-16" if cmd[0] == "clip" else "utf-8"), check=True)
                return True
            except Exception:
                pass
    return False


def gaps(path):
    return path.read_text(encoding="utf-8", errors="ignore").count("[NEEDS INPUT")


# ---------- commands ----------

def cmd_status(_):
    def show(label, paths):
        print(f"{label}: " + (", ".join(p.name for p in paths) if paths else "-"))
    r = ROOT / "resume" / "resume.tex"
    print(f"resume: {'ok' if r.exists() else 'MISSING (python harness.py prompt setup, or /setup)'}")
    ctx = sorted(p for p in (ROOT / "context").iterdir() if p.name != "README.md")
    show("context", ctx)
    if not (ROOT / "context" / "bank.md").exists():
        print("  ! no context/bank.md - output will be generic. Run setup.")
    show("listings (to do)", sorted(p for p in (ROOT / "listings").glob("*.md") if p.name != "README.md"))
    show("listings (done)", sorted((ROOT / "listings" / "completed").glob("*.md")))
    for tex in sorted((ROOT / "output").glob("*.tex")):
        pdf = tex.with_suffix(".pdf").exists()
        print(f"  output/{tex.name}: pdf {'ok' if pdf else 'missing'}, {gaps(tex)} gaps")
    for folder in ("dms", "emails"):
        for p in sorted((ROOT / folder).glob("*.md")):
            if p.name != "README.md":
                print(f"  {folder}/{p.name}: {gaps(p)} gaps")


def cmd_intake(args):
    text = read_in(args[0] if args else None).strip()
    if not text:
        die("empty paste")
    company, role = ask("Company: "), ask("Role: ")
    if not (company and role):
        die("need company and role. Tip: save the listing to a file and run `python harness.py intake listing.txt`")
    url = next(iter(re.findall(r"https?://\S+", text)), "")
    slug = free_slug(slugify(f"{company}-{role}"))
    print("Paste ONLY the short free-text application questions (why us / describe a time...),")
    print("one per line, blank line to finish. Skip name, work auth, EEO, uploads, yes/no, dropdowns:")
    qs = []
    while True:
        line = ask("")
        if not line:
            break
        qs.append(re.sub(r"^\d+[.)]\s*", "", line))
    out = f"---\ncompany: {company}\nrole: {role}\nurl: {url}\ndate_added: {TODAY}\n---\n\n{text}\n"
    if qs:
        out += "\n## Questions\n\n" + "".join(f"{i}. {q}\n" for i, q in enumerate(qs, 1))
    (ROOT / "listings" / f"{slug}.md").write_text(out, encoding="utf-8")
    print(f"wrote listings/{slug}.md")


def context_dump():
    parts, binaries = [], []
    for p in sorted((ROOT / "context").rglob("*")):
        if p.is_file() and p.name != "README.md":
            if p.suffix.lower() in TEXT_EXT:
                parts.append(f"--- context/{p.relative_to(ROOT / 'context').as_posix()} ---\n{p.read_text(encoding='utf-8', errors='ignore')}")
            else:
                binaries.append(p.relative_to(ROOT).as_posix())
    return "\n\n".join(parts), binaries


def cmd_prompt(args):
    if not args:
        die("which task? setup | process <slug> | dm | email | bank")
    task = args[0]
    cmd_file = CMDS / f"{task}.md"
    if not cmd_file.exists():
        die(f"unknown task '{task}'")
    sections = [
        "You are helping me with my job search using the rules and workflow below. "
        "Follow them exactly. Never invent facts about me.",
        FILE_PROTOCOL,
        "# RULES (AGENTS.md)\n\n" + (ROOT / "AGENTS.md").read_text(encoding="utf-8"),
        f"# WORKFLOW: {task}\n\n" + strip_frontmatter(cmd_file.read_text(encoding="utf-8")),
    ]
    if task == "setup":
        for t in ("context-bank.md", "profile.md", "voice.md"):
            sections.append(f"# TEMPLATE: template/{t}\n\n" + (ROOT / "template" / t).read_text(encoding="utf-8"))
        sections.append("# EXAMPLE RESUME LAYOUT: template/examples/resume.tex\n\n" + (ROOT / "template" / "examples" / "resume.tex").read_text(encoding="utf-8"))
    resume = ROOT / "resume" / "resume.tex"
    if resume.exists():
        sections.append("# MY RESUME: resume/resume.tex\n\n" + resume.read_text(encoding="utf-8"))
    elif task != "setup":
        die("no resume/resume.tex yet - run `python harness.py prompt setup` first")
    ctx, binaries = context_dump()
    if ctx:
        sections.append("# MY CONTEXT FILES\n\n" + ctx)
    slug = ""
    if task == "process":
        if len(args) < 2:
            die("process needs a listing slug (python harness.py status lists them)")
        slug = args[1]
        lp = find_listing(slug)
        sections.append(f"# THE LISTING: {lp.relative_to(ROOT).as_posix()} (slug: {slug})\n\n" + lp.read_text(encoding="utf-8"))
        sections.append(f"Do this ONE listing yourself (no subagents). Reply with two FILE blocks: output/{slug}.tex and output/{slug}-changes.md.")
    sections.append("# MY REQUEST\n\n" + TASK_ASK.get(task, "Go."))
    text = "\n\n".join(sections)
    outdir = ROOT / "output" / "prompts"
    outdir.mkdir(exist_ok=True)
    out = outdir / f"{task}{'-' + slug if slug else ''}.txt"
    out.write_text(text, encoding="utf-8")
    print(f"prompt saved: {out.relative_to(ROOT).as_posix()} (~{len(text) // 4:,} tokens)")
    if copy_clipboard(text):
        print("copied to clipboard.")
    if binaries:
        print("attach these yourself (not text):", ", ".join(binaries))
    if "<PASTE HERE>" in text:
        print("replace <PASTE HERE> at the bottom with your info before sending.")
    print("paste into any AI chat (ChatGPT, Gemini, Claude.ai, ...). Save its reply to a file, then:")
    print("  python harness.py apply reply.txt")


def cmd_apply(args):
    text = read_in(args[0] if args else None).replace("\r\n", "\n")
    blocks = FILE_RE.findall(text)
    if not blocks:
        die("no '=== FILE: path ===' ... '=== END FILE ===' blocks found in the reply")
    hook = hook_module()
    for rel, body in blocks:
        rel = rel.strip().strip("`").replace("\\", "/")
        dest = (ROOT / rel).resolve()
        top = Path(rel).parts[0] if Path(rel).parts else ""
        if top not in WRITABLE or ROOT not in dest.parents:
            print(f"SKIPPED {rel}: only {', '.join(WRITABLE)}/ may be written")
            continue
        body = re.sub(r"^```[a-z]*\n|\n```\s*$", "", body)
        dest.parent.mkdir(parents=True, exist_ok=True)
        existed = dest.exists()
        dest.write_text(body.rstrip("\n") + "\n", encoding="utf-8")
        print(f"{'updated' if existed else 'wrote'} {rel}" + (f" ({gaps(dest)} gaps)" if gaps(dest) else ""))
        if dest.suffix == ".tex":
            compile_tex(dest, hook)
            if top == "output":
                for src in [ROOT / "listings" / f"{dest.stem}.md"]:
                    if src.exists():
                        src.rename(ROOT / "listings" / "completed" / src.name)
                        print(f"moved listings/{src.name} -> listings/completed/")


def compile_tex(path, hook=None):
    hook = hook or hook_module()
    if not hook.ensure_latexmk():
        print("  no latexmk - .tex saved, PDF skipped. " + hook.INSTALL_HINT)
        return False
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-cd", str(path)], capture_output=True, text=True)
    log = path.with_suffix(".log")
    err = ""
    if r.returncode and log.exists():
        err = "\n".join(l for l in log.read_text(errors="ignore").splitlines() if l.startswith("!"))[:600]
    hook.clean_junk(str(path))
    print(f"  pdf: {'ok' if r.returncode == 0 else 'FAILED - ' + (err or 'see latexmk output') + ' (open the .tex in Overleaf)'}")
    return r.returncode == 0


def cmd_compile(args):
    p = ROOT / (args[0] if args else "resume/resume.tex")
    if not p.exists():
        die(f"{p} not found")
    sys.exit(0 if compile_tex(p) else 1)


DM_TEMPLATE = """---
handle: "@{name}"
date_drafted: {today}
ask: [NEEDS INPUT: the one ask]
---

## About them
[NEEDS INPUT: paste their bio / the post you're replying to]

## Draft
[NEEDS INPUT: draft]

<!-- checklist (CLAUDE.md/AGENTS.md #14):
- open with THEM: the specific post / thing they built, not your bio
- one fact about you that connects, sourced from your resume/bank
- one ask, easy to say no to; <=60 words (80 max)
- at most one link, bare (no https://)
- avoid: em dashes, "I came across", "I'd love to", "pick your brain",
  "quick question", flattery with no specifics
- copy your voice from context/voice.md -->

## Follow-up (send once after ~5 days)
[NEEDS INPUT: one line, new info if possible]
"""

EMAIL_TEMPLATE = """---
to: [NEEDS INPUT: email]
name: {name}
company: [NEEDS INPUT: company]
subject: [NEEDS INPUT: <=7 words, specific]
status: draft
date_drafted: {today}
---

Hi {first},

[NEEDS INPUT: 1-2 sentences on the specific thing of THEIRS this is about]

[NEEDS INPUT: 1-2 sentences on you that connect to it, facts from your bank]

[NEEDS INPUT: the one ask, e.g. "Would you have 15 minutes in the next two weeks?"]

{signoff}

---
Nothing below this line is sent.

Checklist (AGENTS.md #15): subject <=7 words; body <=150 words; lead with
them; one ask; no attachment; follow up once after ~5 business days;
never two people at one company the same day. Dry run:
python email-app/send.py emails/{slug}.md
"""


def signoff():
    prof = ROOT / "context" / "profile.md"
    if prof.exists():
        m = re.search(r"Email sign-off[^:]*:\s*(.+)", prof.read_text(encoding="utf-8"))
        if m and m.group(1).strip():
            return m.group(1).strip().strip('"').replace("\\n", "\n")
    return "[NEEDS INPUT: sign-off]"


def cmd_new(args):
    if len(args) < 2:
        die("usage: new tailor <slug> | new email <name> | new dm <handle>")
    kind, name = args[0], " ".join(args[1:])
    if kind == "dm":
        h = slugify(name.lstrip("@")).replace("-", "_")
        dest = ROOT / "dms" / f"{h}.md"
        body = DM_TEMPLATE.format(name=name.lstrip("@"), today=TODAY)
    elif kind == "email":
        s = slugify(name)
        dest = ROOT / "emails" / f"{s}.md"
        body = EMAIL_TEMPLATE.format(name=name, first=name.split()[0], today=TODAY, signoff=signoff(), slug=s)
    elif kind == "tailor":
        lp = find_listing(name)
        resume = ROOT / "resume" / "resume.tex"
        if not resume.exists():
            die("no resume/resume.tex")
        listing = lp.read_text(encoding="utf-8")
        qs = re.findall(r"^\d+\.\s*(.+)$", listing.split("## Questions", 1)[1], re.M) if "## Questions" in listing else []
        block = ""
        if qs:
            block = "% ==== APPLICATION ANSWERS (comments only; not compiled) ====\n"
            for i, q in enumerate(qs, 1):
                block += f"% Q{i}: {q}\n% A{i}: [NEEDS INPUT: answer, <150 words, facts from your bank]\n%\n"
            block += "% " + "=" * 60 + "\n"
        tex = ROOT / "output" / f"{name}.tex"
        if tex.exists():
            die(f"output/{name}.tex already exists - edit it directly, or delete it first")
        tex.write_text(block + resume.read_text(encoding="utf-8"), encoding="utf-8")
        (ROOT / "output" / f"{name}-changes.md").write_text(
            f"# Changes: {name}\n\n- [NEEDS INPUT: what you changed and why]\n\n"
            "<!-- Tailoring checklist (AGENTS.md #9): mirror the listing's keywords where TRUE;\n"
            "reorder bullets/projects so the most relevant come first; pull relevant items from\n"
            "context/bank.md; drop irrelevant ones; never add a skill/number you can't back up;\n"
            "keep the same page count. Then: python harness.py compile output/" + name + ".tex -->\n",
            encoding="utf-8")
        print(f"wrote output/{name}.tex (copy of your resume + answer stubs) and output/{name}-changes.md")
        print(f"edit them, then: python harness.py compile output/{name}.tex")
        return
    else:
        die(f"unknown kind '{kind}'")
    if dest.exists():
        die(f"{dest.relative_to(ROOT).as_posix()} already exists")
    dest.write_text(body, encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT).as_posix()} - fill every [NEEDS INPUT: ...]")


def cmd_check(_):
    r = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        die("not a git repo")
    bad = []
    for line in r.stdout.splitlines():
        path = line[3:].strip('"')
        top = path.split("/")[0]
        if top in PERSONAL and not path.endswith(("README.md", ".gitkeep")):
            bad.append(path)
        if path == ".env" or path.endswith(".env"):
            bad.append(path)
    if bad:
        print("PERSONAL FILES VISIBLE TO GIT - do not commit:")
        for b in bad:
            print("  " + b)
        print("fix: add them to .gitignore (and `git rm --cached <file>` if already staged)")
        sys.exit(1)
    print("ok: nothing personal is tracked or staged.")


SHIM = "Read `.claude/commands/{n}.md` and follow it exactly, using the rules in `AGENTS.md`. "\
       "Ignore its frontmatter. `$ARGUMENTS` means: {args}"


def cmd_sync(_):
    names = sorted(p.stem for p in CMDS.glob("*.md"))
    for d in (".gemini/commands", ".cursor/commands", ".github/prompts"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    for n in names:
        desc = re.search(r"^description:\s*(.+)$", (CMDS / f"{n}.md").read_text(encoding="utf-8"), re.M)
        desc = desc.group(1).strip() if desc else n
        (ROOT / ".gemini/commands" / f"{n}.toml").write_text(
            f'description = "{desc.replace(chr(34), chr(39))}"\nprompt = """\n'
            + SHIM.format(n=n, args="{{args}}") + '\n"""\n', encoding="utf-8")
        (ROOT / ".cursor/commands" / f"{n}.md").write_text(
            SHIM.format(n=n, args="whatever I typed after the command") + "\n", encoding="utf-8")
        (ROOT / ".github/prompts" / f"{n}.prompt.md").write_text(
            f"---\ndescription: {desc}\nmode: agent\n---\n"
            + SHIM.format(n=n, args="whatever I typed after the command") + "\n", encoding="utf-8")
    print(f"synced {len(names)} commands: {', '.join(names)}")


COMMANDS = {"status": cmd_status, "intake": cmd_intake, "prompt": cmd_prompt, "apply": cmd_apply,
            "new": cmd_new, "compile": cmd_compile, "check": cmd_check, "sync": cmd_sync}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(0 if len(sys.argv) < 2 else 1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
