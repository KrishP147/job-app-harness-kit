#!/usr/bin/env python3
"""PostToolUse hook: auto-compile .tex files under resume/ or output/.

Reads the hook JSON payload on stdin, and if the edited/written file is a
.tex file under resume/ or output/ (relative to the project root), runs
latexmk to build the PDF and cleans up LaTeX build junk.

Contract: always exits 0. Never blocks a tool call. Silent for
non-matching files. Only when there's something to report (latexmk
missing, or compile failed) prints JSON on stdout: top-level
`systemMessage` (shown to the user) + PostToolUse
`hookSpecificOutput.additionalContext` (shown to Claude), same text.

If latexmk isn't on PATH (e.g. Claude Code was launched before MiKTeX was
installed), probes the usual install dirs (MiKTeX, Strawberry Perl, TeX
Live, MacTeX) and prepends them to PATH before giving up.

Launched from .claude/settings.json as `python3 ... || python ...`.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import time

# /process creates this marker while its subagents own compiling; ignored
# if older than MARKER_MAX_AGE (stale marker from a crashed session).
MARKER = os.path.join("output", ".processing")
MARKER_MAX_AGE = 2 * 60 * 60

JUNK_EXTS = [".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".synctex.gz"]

INSTALL_HINT = (
    "Install latexmk: Windows `winget install MiKTeX.MiKTeX` + "
    "`winget install StrawberryPerl.StrawberryPerl`; "
    "Mac `brew install --cask basictex && sudo tlmgr install latexmk`; "
    "Linux `sudo apt install texlive-latex-extra latexmk`."
)


def ensure_latexmk():
    """True if latexmk is runnable, after probing known install dirs."""
    if shutil.which("latexmk"):
        return True
    dirs = []
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        dirs += [
            os.path.join(local, "Programs", "MiKTeX", "miktex", "bin", "x64"),
            "C:/Program Files/MiKTeX/miktex/bin/x64",
            "C:/Strawberry/perl/bin",  # MiKTeX's latexmk needs perl
        ]
        dirs += glob.glob("C:/texlive/*/bin/windows")
        dirs += glob.glob("C:/texlive/*/bin/win32")
    else:
        dirs += ["/Library/TeX/texbin", "/opt/homebrew/bin", "/usr/local/bin"]
        dirs += glob.glob("/usr/local/texlive/*/bin/*")
    found = [d for d in dirs if d and os.path.isdir(d)]
    if found:
        os.environ["PATH"] = os.pathsep.join(found + [os.environ.get("PATH", "")])
    return shutil.which("latexmk") is not None


def emit(message):
    print(json.dumps({
        "systemMessage": message,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        },
    }))


def clean_junk(tex_path):
    base, _ = os.path.splitext(tex_path)
    for ext in JUNK_EXTS:
        junk = base + ext
        try:
            if os.path.isfile(junk):
                os.remove(junk)
        except OSError:
            pass


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not file_path:
        return

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    project_dir = os.path.abspath(project_dir)

    file_path_norm = file_path.replace("\\", "/")
    if os.path.isabs(file_path) or (len(file_path_norm) > 1 and file_path_norm[1] == ":"):
        file_abs = os.path.abspath(file_path)
    else:
        file_abs = os.path.abspath(os.path.join(project_dir, file_path))

    if not file_abs.lower().endswith(".tex"):
        return

    try:
        rel = os.path.relpath(file_abs, project_dir)
    except ValueError:
        # Different drives on Windows (e.g. project on C:, file on D:).
        return
    rel_norm = rel.replace("\\", "/")

    if rel_norm.startswith(".."):
        return
    if not (rel_norm.startswith("resume/") or rel_norm.startswith("output/")):
        return

    if os.environ.get("JOB_HARNESS_NO_HOOK") == "1":
        return
    marker = os.path.join(project_dir, MARKER)
    try:
        if time.time() - os.path.getmtime(marker) < MARKER_MAX_AGE:
            return
    except OSError:
        pass

    if not ensure_latexmk():
        emit(
            f"latexmk not found; {rel_norm} saved, PDF not built. " + INSTALL_HINT
        )
        return

    try:
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-cd", file_abs],
            capture_output=True,
            text=True,
            timeout=120,
        )
        ok = result.returncode == 0
    except Exception:
        ok = False

    clean_junk(file_abs)

    if not ok:
        emit(
            f"latexmk failed compiling {rel_norm} — open the file, fix the "
            "LaTeX error, and save again to retry."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
