#!/usr/bin/env bash
# Source this: puts latexmk on PATH if it's installed but the shell that
# launched us predates the install (common after `winget install`).
# Returns 0 if latexmk is usable afterwards, 1 if not.
ensure_latexmk() {
  command -v latexmk >/dev/null 2>&1 && return 0
  local la="${LOCALAPPDATA:-}"
  if [ -n "$la" ] && command -v cygpath >/dev/null 2>&1; then
    la="$(cygpath -u "$la" 2>/dev/null || echo "$la")"
  fi
  local d
  for d in \
    "$la/Programs/MiKTeX/miktex/bin/x64" \
    "/c/Program Files/MiKTeX/miktex/bin/x64" \
    "/c/Strawberry/perl/bin" \
    /c/texlive/*/bin/windows \
    /c/texlive/*/bin/win32 \
    /Library/TeX/texbin \
    /usr/local/texlive/*/bin/* \
    /opt/homebrew/bin; do
    [ -d "$d" ] && PATH="$d:$PATH"
  done
  export PATH
  command -v latexmk >/dev/null 2>&1
}
