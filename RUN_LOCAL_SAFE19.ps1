$ErrorActionPreference="Stop"
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here
python -m pip install -r requirements.txt
python scripts\validate_deployment.py
if ($LASTEXITCODE -ne 0) { throw "SAFE19 validation failed." }
python -m streamlit run app.py
