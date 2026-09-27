[CmdletBinding()]
param(
    [switch]$Quick
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==> Checking Python Environment & Dependencies"
python --version
if ($LASTEXITCODE -ne 0) {
    throw "Python not available"
}

Write-Host "==> Running Test Suite & Integrity Checks"
python -m pytest tests -q
if ($LASTEXITCODE -ne 0) {
    throw "Test suite failed with exit code $LASTEXITCODE"
}

Write-Host "==> Checking Upstream Baseline & Updates"
python tools/check_upstream_updates.py --strict
if ($LASTEXITCODE -ne 0) {
    throw "Upstream check failed with exit code $LASTEXITCODE"
}

Write-Host "WINDOWS DEV CHECK GREEN"

