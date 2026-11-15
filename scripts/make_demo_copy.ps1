<#
.SYNOPSIS
    Provisions an independent demonstration copy of PredictIQ at E:\Codex\PredictIQ-demo.
.DESCRIPTION
    Creates an immutable git worktree checked out at the specified tag, copies configuration
    files, runtime virtual environment (.venv), and frontend dependencies (node_modules),
    then validates the demo copy using preflight.ps1.
.PARAMETER Tag
    The git tag or commit SHA to check out (e.g. dev3-green-01).
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$Tag = "dev3-green-01"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$DemoRoot = "E:\Codex\PredictIQ-demo"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                 PROVISIONING PREDICTIQ DEMONSTRATION WORKTREE                  " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Source Repository : $RepoRoot"
Write-Host "Target Directory  : $DemoRoot"
Write-Host "Target Tag        : $Tag"
Write-Host ""

# 1. Clean existing demo worktree or directory if present
if (Test-Path $DemoRoot) {
    Write-Host "[1/5] Removing existing worktree at $DemoRoot..." -ForegroundColor Yellow
    & git worktree remove --force $DemoRoot 2>&1 | Out-Null
    if (Test-Path $DemoRoot) {
        Remove-Item -Path $DemoRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
& git worktree prune 2>&1 | Out-Null

# 2. Add git worktree at specified tag
Write-Host "[2/5] Creating detached git worktree at tag '$Tag'..." -ForegroundColor Cyan
& git worktree add --detach $DemoRoot $Tag
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create git worktree at tag '$Tag'."
    exit 1
}

# 3. Copy environment and secret configuration files
Write-Host "[3/5] Copying local configuration and service account credentials..." -ForegroundColor Cyan
Copy-Item (Join-Path $RepoRoot "backend\.env") (Join-Path $DemoRoot "backend\.env") -Force
Copy-Item (Join-Path $RepoRoot "frontend\.env") (Join-Path $DemoRoot "frontend\.env") -Force

$backendCreds = Join-Path $RepoRoot "backend\firebase-service-account.json"
if (Test-Path $backendCreds) {
    Copy-Item $backendCreds (Join-Path $DemoRoot "backend\firebase-service-account.json") -Force
}

# 4. Copy runtime environments (.venv and node_modules) using robocopy
Write-Host "[4/5] Syncing Python virtual environment and Node modules..." -ForegroundColor Cyan

$srcVenv = Join-Path $RepoRoot ".venv"
$dstVenv = Join-Path $DemoRoot ".venv"
if (Test-Path $srcVenv) {
    Write-Host "  Syncing .venv with robocopy..." -NoNewline
    robocopy $srcVenv $dstVenv /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    Write-Host " done." -ForegroundColor Green
}

$srcModules = Join-Path $RepoRoot "frontend\node_modules"
$dstModules = Join-Path $DemoRoot "frontend\node_modules"
if (Test-Path $srcModules) {
    Write-Host "  Syncing frontend\node_modules with robocopy..." -NoNewline
    robocopy $srcModules $dstModules /E /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    Write-Host " done." -ForegroundColor Green
}

# 5. Execute preflight verification in demo copy
Write-Host "[5/5] Executing preflight audit on the demo copy..." -ForegroundColor Cyan
Set-Location $DemoRoot
& powershell -ExecutionPolicy Bypass -File (Join-Path $DemoRoot "scripts\preflight.ps1")
$preflightCode = $LASTEXITCODE

Set-Location $RepoRoot

if ($preflightCode -eq 0) {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "             DEMONSTRATION COPY PROVISIONED & VERIFIED SUCCESSFULLY!            " -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "Location: $DemoRoot" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the demo directly from the dedicated worktree:" -ForegroundColor Yellow
    Write-Host "  cd E:\Codex\PredictIQ-demo" -ForegroundColor White
    Write-Host "  pwsh scripts/start_demo.ps1" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Error "Demo copy preflight check failed. Review errors above."
    exit 1
}
