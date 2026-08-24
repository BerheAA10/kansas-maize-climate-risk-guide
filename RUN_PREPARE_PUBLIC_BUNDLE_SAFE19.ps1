$ErrorActionPreference="Stop"
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here
python scripts\validate_deployment.py
if ($LASTEXITCODE -ne 0) { throw "SAFE19 validation failed." }
python scripts\prepare_public_bundle_from_H_drive.py
if ($LASTEXITCODE -ne 0) { throw "SAFE19 public bundle export failed." }
