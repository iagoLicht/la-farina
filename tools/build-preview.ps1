# Builds a preview copy of the site for publishing as a Claude Artifact.
#
# index.html is the real, deployable website. The Artifact viewer supplies
# its own <!doctype>/<html>/<head>/<body> skeleton, so this script strips ours
# out and writes the remainder to a temp file.
#
# Usage:  powershell -ExecutionPolicy Bypass -File tools\build-preview.ps1

param([string]$Out = (Join-Path $env:TEMP "lafarina-preview.html"))

$src = Join-Path $PSScriptRoot "..\index.html"
if (-not (Test-Path $src)) { throw "cannot find $src" }

$t = [IO.File]::ReadAllText($src)

$headStart = $t.IndexOf("<title>")
$headEnd   = $t.IndexOf("</head>")
$bodyOpen  = $t.IndexOf("<body>")
$bodyEnd   = $t.LastIndexOf("</body>")
if ($headStart -lt 0 -or $headEnd -lt 0 -or $bodyOpen -lt 0 -or $bodyEnd -lt 0) {
    throw "index.html is missing the expected head/body structure"
}
$bodyStart = $bodyOpen + "<body>".Length

$head = $t.Substring($headStart, $headEnd - $headStart)
$body = $t.Substring($bodyStart, $bodyEnd - $bodyStart)

[IO.File]::WriteAllText($Out, ($head.TrimEnd() + "`n" + $body), (New-Object Text.UTF8Encoding $false))
Write-Output "preview written: $Out"
