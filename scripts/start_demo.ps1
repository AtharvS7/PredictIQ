<#
.SYNOPSIS
    Starts the PredictIQ demonstration environment (Backend on port 8010, Frontend on port 5173).
.DESCRIPTION
    Runs preflight checks, starts the FastAPI backend on port 8010, waits for the /ready endpoint,
    then launches the Vite frontend configured to communicate with the demo backend.
#>

[CmdletBinding()]
param (
    [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$agentDir = Join-Path $RepoRoot ".agent"
if (-not (Test-Path $agentDir)) { New-Item -ItemType Directory -Path $agentDir | Out-Null }

if (-not $SkipPreflight) {
    Write-Host "[1/3] Running system preflight checks..." -ForegroundColor Cyan
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "preflight.ps1")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Preflight checks failed. Correct the reported errors before starting demo."
        exit 1
    }
}

Write-Host "[2/3] Launching FastAPI backend on port 8010..." -ForegroundColor Cyan
$pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$backendDir = Join-Path $RepoRoot "backend"
$backendOutLog = Join-Path $agentDir "backend_demo_out.log"
$backendErrLog = Join-Path $agentDir "backend_demo_err.log"

$backendProc = Start-Process -FilePath $pythonExe `
    -ArgumentList "-u", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8010", "--no-access-log" `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput $backendOutLog `
    -RedirectStandardError $backendErrLog `
    -PassThru

# Wait for backend readiness (/api/v1/ready)
$readyUrl = "http://127.0.0.1:8010/api/v1/ready"
$ready = $false
$attempts = 0
$maxAttempts = 30

Write-Host "Waiting for backend readiness at $readyUrl..." -NoNewline
while (-not $ready -and $attempts -lt $maxAttempts) {
    Start-Sleep -Seconds 1
    $attempts++
    Write-Host "." -NoNewline
    try {
        $response = Invoke-RestMethod -Uri $readyUrl -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response -and $response.status -eq "healthy") {
            $ready = $true
        }
    } catch {
        # Backend still starting up
    }
}
Write-Host ""

if (-not $ready) {
    Write-Error "Backend did not become ready within 30 seconds. Check logs at .agent\backend_demo_err.log"
    Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend is ready! (HTTP 200 - Healthy)" -ForegroundColor Green

Write-Host "[3/3] Launching Vite frontend on port 5173..." -ForegroundColor Cyan
$env:VITE_API_BASE_URL = "http://localhost:8010/api/v1"
$frontendDir = Join-Path $RepoRoot "frontend"
$frontendOutLog = Join-Path $agentDir "frontend_demo_out.log"
$frontendErrLog = Join-Path $agentDir "frontend_demo_err.log"

$frontendProc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", "npx vite" `
    -WorkingDirectory $frontendDir `
    -RedirectStandardOutput $frontendOutLog `
    -RedirectStandardError $frontendErrLog `
    -PassThru

# Save PIDs for clean shutdown
$pids = @{
    backend_pid = $backendProc.Id
    frontend_pid = $frontendProc.Id
    backend_port = 8010
    frontend_port = 5173
    started_at = (Get-Date).ToString("o")
}
$pids | ConvertTo-Json | Set-Content (Join-Path $agentDir "demo_pids.json")

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "                    PREDICTIQ DEMO ENVIRONMENT IS READY!                        " -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "  Frontend Application : http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend Swagger API  : http://localhost:8010/docs" -ForegroundColor Cyan
Write-Host "  Readiness Probe      : http://localhost:8010/api/v1/ready" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "To stop the demo cleanly, run:" -ForegroundColor Yellow
Write-Host "  pwsh scripts/stop_demo.ps1" -ForegroundColor Yellow
Write-Host ""
