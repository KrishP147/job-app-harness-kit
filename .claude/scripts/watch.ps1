# Watch resume/ and output/ .tex files, recompiling live on manual edits.
# Opt-in: run this yourself when editing .tex outside Claude Code (the
# PostToolUse hook already covers edits made through Claude Code).

. "$PSScriptRoot\latexmk_env.ps1"
if (-not (Ensure-Latexmk)) {
    Write-Error "latexmk not found on PATH. Install it: Windows 'winget install MiKTeX.MiKTeX' + 'winget install StrawberryPerl.StrawberryPerl'; Mac 'brew install --cask basictex && sudo tlmgr install latexmk'; Linux 'sudo apt install texlive-latex-extra latexmk'."
    exit 1
}

$targets = @()
$targets += Get-ChildItem -Path "resume" -Filter "*.tex" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
$targets += Get-ChildItem -Path "output" -Filter "*.tex" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }

if ($targets.Count -eq 0) {
    Write-Error "no .tex files found under resume/ or output/."
    exit 1
}

Write-Host "Watching resume/*.tex and output/*.tex - Ctrl+C to stop."

$procs = @()
try {
    foreach ($f in $targets) {
        $procs += Start-Process -FilePath "latexmk" -ArgumentList @("-cd", "-pvc", "-pdf", "-view=none", "-interaction=nonstopmode", "`"$f`"") -NoNewWindow -PassThru
    }
    Wait-Process -Id ($procs | ForEach-Object { $_.Id }) -ErrorAction SilentlyContinue
}
finally {
    foreach ($p in $procs) {
        try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
}
