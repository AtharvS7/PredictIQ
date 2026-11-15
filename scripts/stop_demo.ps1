<#
.SYNOPSIS
    Stops the PredictIQ demonstration environment cleanly.
.DESCRIPTION
    Terminates backend (port 8010) and frontend (port 5173) processes started by start_demo.ps1.
#>

[CmdletBinding()]
param ()

$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$pidsFile = Join-Path $RepoRoot ".agent\demo_pids.json"
$stopped = 0

if (Test-Path $pidsFile) {
    try {
        $pids = Get-Content $pidsFile -Raw | ConvertFrom-Json
        if ($pids.backend_pid) {
            Write-Host "Stopping backend process (PID $($pids.backend_pid))..." -ForegroundColor Cyan
            Stop-Process -Id $pids.backend_pid -Force -ErrorAction SilentlyContinue
            $stopped++
        }
        if ($pids.frontend_pid) {
            Write-Host "Stopping frontend process (PID $($pids.frontend_pid))..." -ForegroundColor Cyan
            # On Windows, stop tree for cmd.exe / npm
            & taskkill /PID $pids.frontend_pid /T /F 2>&1 | Out-Null
            $stopped++
        }
        Remove-Item $pidsFile -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Warning "Could not parse demo_pids.json: $_"
    }
}

# Fallback check for listeners on port 8010
$conn8010 = Get-NetTCPConnection -LocalPort 8010 -ErrorAction SilentlyContinue
if ($conn8010) {
    foreach ($c in $conn8010) {
        if ($c.OwningProcess -gt 0) {
            Write-Host "Releasing port 8010 (PID $($c.OwningProcess))..." -ForegroundColor Cyan
            Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
            $stopped++
        }
    }
}

Write-Host "PredictIQ demonstration processes stopped successfully ($stopped process(es) terminated)." -ForegroundColor Green
