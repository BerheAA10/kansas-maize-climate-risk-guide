$ErrorActionPreference = "Stop"

$SearchRoot = Join-Path $HOME "Downloads"

$Public = Get-ChildItem -LiteralPath $SearchRoot `
    -Recurse `
    -Directory `
    -Filter "*SAFE19_FIX08_PUBLIC_BUNDLE_*" `
    -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Public) {
    throw "No SAFE19_FIX08 public bundle was found under Downloads."
}

Write-Host "FOUND PUBLIC BUNDLE:" -ForegroundColor Green
Write-Host $Public.FullName

Set-Location -LiteralPath $Public.FullName

& python ".\scripts\validate_deployment.py"
if ($LASTEXITCODE -ne 0) {
    throw "Public-bundle validation failed."
}

Write-Host "Opening existing SAFE19_FIX08 public bundle on http://localhost:8506" -ForegroundColor Green
& python -m streamlit run app.py --server.port 8506
