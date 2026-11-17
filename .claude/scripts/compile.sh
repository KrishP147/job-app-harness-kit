#!/usr/bin/env bash
# Manually compile a .tex file to PDF and clean up build junk.
# Usage: .claude/scripts/compile.sh [path/to/file.tex]   (default: resume/resume.tex)
set -uo pipefail

TARGET="${1:-resume/resume.tex}"

# shellcheck source=latexmk_env.sh
. "$(dirname "${BASH_SOURCE[0]}")/latexmk_env.sh"
if ! ensure_latexmk; then
  echo "error: latexmk not found on PATH." >&2
  echo "Install it: Windows 'winget install MiKTeX.MiKTeX' + 'winget install StrawberryPerl.StrawberryPerl'; Mac 'brew install --cask basictex && sudo tlmgr install latexmk'; Linux 'sudo apt install texlive-latex-extra latexmk'." >&2
  exit 1
fi

if [ ! -f "$TARGET" ]; then
  echo "error: $TARGET not found." >&2
  exit 1
fi

latexmk -pdf -interaction=nonstopmode -cd "$TARGET"
STATUS=$?

BASE="${TARGET%.tex}"
for ext in aux log out fls fdb_latexmk synctex.gz; do
  rm -f "${BASE}.${ext}"
done

exit "$STATUS"
