# Dot-source this: puts latexmk on PATH if it's installed but the shell that
# launched us predates the install (common after `winget install`).
function Ensure-Latexmk {
    if (Get-Command latexmk -ErrorAction SilentlyContinue) { return $true }
    $dirs = @(
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64",
        "C:\Program Files\MiKTeX\miktex\bin\x64",
        "C:\Strawberry\perl\bin"
    )
    $dirs += Get-ChildItem "C:\texlive\*\bin\windows" -Directory -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
    foreach ($d in $dirs) {
        if ($d -and (Test-Path $d)) { $env:Path = "$d;$env:Path" }
    }
    return [bool](Get-Command latexmk -ErrorAction SilentlyContinue)
}
