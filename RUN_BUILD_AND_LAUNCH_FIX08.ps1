$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

Write-Host "SAFE19_FIX08 — validating source package" -ForegroundColor Cyan
python .\scripts\validate_deployment.py
if ($LASTEXITCODE -ne 0) { throw "SAFE19_FIX08 validation failed." }

$Before = @(Get-ChildItem $Here.Directory.FullName -Directory -Filter "*SAFE19_FIX08_PUBLIC_BUNDLE_*" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)

Write-Host "SAFE19_FIX08 — creating a new public bundle" -ForegroundColor Cyan
python .\scripts\prepare_public_bundle_from_H_drive.py
if ($LASTEXITCODE -ne 0) { throw "SAFE19_FIX08 public-bundle export failed." }

$Public = Get-ChildItem $Here.Directory.FullName -Directory -Filter "*SAFE19_FIX08_PUBLIC_BUNDLE_*" |
    Where-Object { $_.FullName -notin $Before } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Public) {
    $Public = Get-ChildItem $Here.Directory.FullName -Directory -Filter "*SAFE19_FIX08_PUBLIC_BUNDLE_*" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

if (-not $Public) { throw "Could not locate the SAFE19_FIX08 public bundle." }

Write-Host "RUNNING PUBLIC BUNDLE:" -ForegroundColor Green
Write-Host $Public.FullName
Set-Location $Public.FullName
python .\scripts\validate_deployment.py
if ($LASTEXITCODE -ne 0) { throw "Public-bundle validation failed." }

Write-Host "Opening SAFE19_FIX08 on http://localhost:8505" -ForegroundColor Green
python -m streamlit run app.py --server.port 8505
