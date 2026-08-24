$ErrorActionPreference = "Stop"

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Parent = Split-Path -Parent $Here
Set-Location $Here

Write-Host "SAFE19_FIX11 - validating source package" -ForegroundColor Cyan
& python ".\scripts\validate_deployment.py"
if ($LASTEXITCODE -ne 0) {
    throw "SAFE19_FIX11 validation failed."
}

Write-Host "SAFE19_FIX11 - creating a new public bundle" -ForegroundColor Cyan

$ExportLines = @(
    & python ".\scripts\prepare_public_bundle_from_H_drive.py" 2>&1 |
        ForEach-Object {
            $line = $_.ToString()
            Write-Host $line
            $line
        }
)

if ($LASTEXITCODE -ne 0) {
    throw "SAFE19_FIX11 public-bundle export failed."
}

$PublicPath = $null

foreach ($line in $ExportLines) {
    if ($line -match '^\s*Output:\s*(.+?)\s*$') {
        $candidate = $Matches[1].Trim()
        if (Test-Path -LiteralPath $candidate -PathType Container) {
            $PublicPath = (Resolve-Path -LiteralPath $candidate).Path
        }
    }
}

if (-not $PublicPath) {
    $Public = Get-ChildItem -LiteralPath $Parent `
        -Directory `
        -Filter "*SAFE19_FIX11_PUBLIC_BUNDLE_*" `
        -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($Public) {
        $PublicPath = $Public.FullName
    }
}

if (-not $PublicPath) {
    throw "Could not locate the SAFE19_FIX11 public bundle after export."
}

Write-Host ""
Write-Host "RUNNING PUBLIC BUNDLE:" -ForegroundColor Green
Write-Host $PublicPath

Set-Location -LiteralPath $PublicPath

& python ".\scripts\validate_deployment.py"
if ($LASTEXITCODE -ne 0) {
    throw "Public-bundle validation failed."
}

Write-Host ""
Write-Host "Opening SAFE19_FIX11 on http://localhost:8509" -ForegroundColor Green
& python -m streamlit run app.py --server.port 8509
