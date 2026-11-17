#!/usr/bin/env bash
# Watch resume/ and output/ .tex files, recompiling live on manual edits.
# Opt-in: run this yourself when editing .tex outside Claude Code (the
# PostToolUse hook already covers edits made through Claude Code).
set -uo pipefail

# shellcheck source=latexmk_env.sh
. "$(dirname "${BASH_SOURCE[0]}")/latexmk_env.sh"
if ! ensure_latexmk; then
  echo "error: latexmk not found on PATH." >&2
  echo "Install it: Windows 'winget install MiKTeX.MiKTeX' + 'winget install StrawberryPerl.StrawberryPerl'; Mac 'brew install --cask basictex && sudo tlmgr install latexmk'; Linux 'sudo apt install texlive-latex-extra latexmk'." >&2
  exit 1
fi

echo "Watching resume/*.tex and output/*.tex — Ctrl+C to stop."

shopt -s nullglob
TARGETS=(resume/*.tex output/*.tex)
shopt -u nullglob

if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "error: no .tex files found under resume/ or output/." >&2
  exit 1
fi

trap 'trap - INT TERM; kill 0' INT TERM

for f in "${TARGETS[@]}"; do
  latexmk -cd -pvc -pdf -view=none -interaction=nonstopmode "$f" &
done

wait
