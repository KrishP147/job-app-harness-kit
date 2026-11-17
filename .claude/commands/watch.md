---
description: Watch resume/ and output/ .tex files and recompile on save
argument-hint: (no arguments)
allowed-tools: Bash
---

Run `.claude/scripts/watch.sh` (or `.claude/scripts/watch.ps1` on Windows) in the
foreground. This is opt-in, for when the user is editing `.tex` files
directly (outside Claude Code) and wants live recompilation — edits made
through Claude Code already auto-compile via the PostToolUse hook.

If `latexmk` isn't installed, the script will say so; point the user at
the README's install command for their OS.

Target list (`resume/*.tex` + `output/*.tex`) is fixed at startup, one
`latexmk -cd -pvc` process per file, PDF lands beside its `.tex`. A new
`output/*.tex` added after start needs a restart to be picked up.
