# Manually compile a .tex file to PDF and clean up build junk.
# Usage: .claude/scripts/compile.ps1 [path/to/file.tex]   (default: resume/resume.tex)

param(
    [string]$Target = "resume/resume.tex"
)

. "$PSScriptRoot\latexmk_env.ps1"
if (-not (Ensure-Latexmk)) {
    Write-Error "latexmk not found on PATH. Install it: Windows 'winget install MiKTeX.MiKTeX' + 'winget install StrawberryPerl.StrawberryPerl'; Mac 'brew install --cask basictex && sudo tlmgr install latexmk'; Linux 'sudo apt install texlive-latex-extra latexmk'."
    exit 1
}

if (-not (Test-Path $Target)) {
    Write-Error "$Target not found."
    exit 1
}

latexmk -pdf -interaction=nonstopmode -cd $Target
$exitCode = $LASTEXITCODE

$base = $Target -replace '\.tex$', ''
foreach ($ext in @("aux", "log", "out", "fls", "fdb_latexmk", "synctex.gz")) {
    $junk = "$base.$ext"
    if (Test-Path $junk) {
        Remove-Item -Force $junk
    }
}

exit $exitCode
