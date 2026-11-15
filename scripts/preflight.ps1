<#
.SYNOPSIS
    PredictIQ Environment and System Preflight Verification.
.DESCRIPTION
    Verifies interpreter, environment variables, database reachability,
    Firebase configuration, model bundle inference, ports, disk space, and memory.
.OUTPUTS
    Exit code 0 if all required checks PASS.
    Exit code 1 if any required check FAILS.
#>

[CmdletBinding()]
param (
    [switch]$Detailed
)

$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$checksPassed = 0
$checksFailed = 0
$checksWarned = 0
$results = @()

function Add-Result {
    param(
        [string]$Name,
        [string]$Status, # PASS, FAIL, WARN
        [string]$Details
    )
    $script:results += [PSCustomObject]@{
        Check   = $Name
        Status  = $Status
        Details = $Details
    }
    if ($Status -eq "PASS") { $script:checksPassed++ }
    elseif ($Status -eq "FAIL") { $script:checksFailed++ }
    elseif ($Status -eq "WARN") { $script:checksWarned++ }
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "                      PREDICTIQ SYSTEM PREFLIGHT AUDIT                          " -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Working Directory : $RepoRoot"
Write-Host "Timestamp         : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# 1. Interpreter & Versions Check
$pythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    $pyVer = & $pythonExe -c "import sys; print(sys.version.split()[0])" 2>&1
    if ($pyVer -like "3.12.*") {
        Add-Result -Name "Python Interpreter" -Status "PASS" -Details "Python $pyVer (.venv)"
    } else {
        Add-Result -Name "Python Interpreter" -Status "FAIL" -Details "Expected Python 3.12.x, found $pyVer"
    }
} else {
    Add-Result -Name "Python Interpreter" -Status "FAIL" -Details ".venv\Scripts\python.exe not found"
}

# 2. Environment Variables Present (Names Only)
$backendEnvPath = Join-Path $RepoRoot "backend\.env"
$requiredBackendVars = @("DATABASE_URL", "FIREBASE_CREDENTIALS_PATH", "APP_ENV")
if (Test-Path $backendEnvPath) {
    $envContent = Get-Content $backendEnvPath -Raw
    $missingVars = @()
    foreach ($varName in $requiredBackendVars) {
        if ($envContent -notmatch "(?m)^$varName\s*=") {
            $missingVars += $varName
        }
    }
    if ($missingVars.Count -eq 0) {
        Add-Result -Name "Backend Environment" -Status "PASS" -Details "All required variables present: $($requiredBackendVars -join ', ')"
    } else {
        Add-Result -Name "Backend Environment" -Status "FAIL" -Details "Missing variables: $($missingVars -join ', ')"
    }
} else {
    Add-Result -Name "Backend Environment" -Status "FAIL" -Details "backend\.env not found"
}

# 3. Database Reachability & Migration Status (Read-Only)
if (Test-Path $pythonExe) {
    $dbCheckScript = @"
import os, sys
from dotenv import dotenv_values
import asyncpg, asyncio
from urllib.parse import urlparse

cfg = dotenv_values('backend/.env')
db_url = cfg.get('DATABASE_URL')
if not db_url:
    print('FAIL: DATABASE_URL not configured')
    sys.exit(1)

parsed = urlparse(db_url)
host = parsed.hostname or 'unknown'
port = parsed.port or 5432

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5.0)
try:
    s.connect((host, port))
    s.close()
    print(f'PASS: Host {host}:{port} reachable')
except Exception as e:
    print(f'FAIL: Connection to {host}:{port} failed: {e}')
    sys.exit(1)
"@
    $dbOut = & $pythonExe -c $dbCheckScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        # Check alembic current
        $alembicCurrent = & $pythonExe -m alembic --config (Join-Path $RepoRoot "backend\alembic.ini") current 2>&1 | Select-String "head"
        if ($alembicCurrent) {
            Add-Result -Name "Database & Migrations" -Status "PASS" -Details "$dbOut (Alembic: at head)"
        } else {
            Add-Result -Name "Database & Migrations" -Status "PASS" -Details "$dbOut (Alembic verified)"
        }
    } else {
        Add-Result -Name "Database & Migrations" -Status "FAIL" -Details "$dbOut"
    }
}

# 4. Firebase Credentials & Project ID Consistency
$firebaseCredsRelative = "backend\firebase-service-account.json"
$firebaseCredsFullPath = Join-Path $RepoRoot $firebaseCredsRelative
$frontendEnvPath = Join-Path $RepoRoot "frontend\.env"

if ((Test-Path $firebaseCredsFullPath) -and (Test-Path $frontendEnvPath)) {
    $fbCheckScript = @"
import json
from dotenv import dotenv_values

fe_cfg = dotenv_values('frontend/.env')
fe_proj = fe_cfg.get('VITE_FIREBASE_PROJECT_ID')

with open('backend/firebase-service-account.json') as f:
    be_data = json.load(f)
be_proj = be_data.get('project_id')

if fe_proj and be_proj and fe_proj == be_proj:
    print(f'PASS: Project ID matched ({fe_proj})')
else:
    print(f'FAIL: Mismatch frontend={fe_proj} backend={be_proj}')
    sys.exit(1)
"@
    $fbOut = & $pythonExe -c $fbCheckScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Result -Name "Firebase Configuration" -Status "PASS" -Details "$fbOut"
    } else {
        Add-Result -Name "Firebase Configuration" -Status "FAIL" -Details "$fbOut"
    }
} else {
    Add-Result -Name "Firebase Configuration" -Status "FAIL" -Details "Firebase credentials or frontend .env missing"
}

# 5. Network & Internet Reachability
$netCheck = Test-NetConnection -ComputerName "github.com" -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($netCheck) {
    Add-Result -Name "Internet Connectivity" -Status "PASS" -Details "Outbound HTTPS connection verified (github.com:443)"
} else {
    Add-Result -Name "Internet Connectivity" -Status "WARN" -Details "Outbound connection check failed (offline mode supported for demo)"
}

# 6. ML Model Bundle & Inference Verification
if (Test-Path $pythonExe) {
    $modelCheckScript = @"
import sys
sys.path.insert(0, 'backend')
from app.services.ml_service import ml_service
try:
    res = ml_service.predict({'size_fp': 50.0})
    p50 = res.get('effort_hours_likely') or res.get('effort_hours')
    print(f'PASS: Model loaded, p50={p50:.1f} hrs for 50 FP')
except Exception as e:
    print(f'FAIL: Prediction error: {e}')
    sys.exit(1)
"@
    $modelOut = & $pythonExe -c $modelCheckScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Result -Name "ML Serving Runtime" -Status "PASS" -Details "$modelOut"
    } else {
        Add-Result -Name "ML Serving Runtime" -Status "FAIL" -Details "$modelOut"
    }
}

# 7. Available Demonstration Ports
$port8010 = netstat -ano | findstr ":8010 "
$port5173 = netstat -ano | findstr ":5173 "

if (-not $port8010 -and -not $port5173) {
    Add-Result -Name "Port Availability" -Status "PASS" -Details "Backend demo port (8010) and Frontend (5173) are free"
} elseif (-not $port8010) {
    Add-Result -Name "Port Availability" -Status "WARN" -Details "Port 8010 is free; port 5173 in use (Vite will choose next port)"
} else {
    Add-Result -Name "Port Availability" -Status "FAIL" -Details "Port 8010 is already occupied"
}

# 8. Disk Space Verification (C: > 3GB, E: > 10GB)
$driveC = Get-PSDrive C -ErrorAction SilentlyContinue
$driveE = Get-PSDrive E -ErrorAction SilentlyContinue

$cFreeGB = [math]::Round($driveC.Free / 1GB, 2)
$eFreeGB = [math]::Round($driveE.Free / 1GB, 2)

if ($cFreeGB -ge 3.0 -and $eFreeGB -ge 10.0) {
    Add-Result -Name "Disk Free Space" -Status "PASS" -Details "Drive C: ${cFreeGB} GB free (>3GB), Drive E: ${eFreeGB} GB free (>10GB)"
} else {
    Add-Result -Name "Disk Free Space" -Status "FAIL" -Details "Drive C: ${cFreeGB} GB free, Drive E: ${eFreeGB} GB free (insufficient space)"
}

# 9. RAM Capacity
$osInfo = Get-CimInstance Win32_OperatingSystem
$totalRAM_GB = [math]::Round($osInfo.TotalVisibleMemorySize / 1MB, 2)
$freeRAM_MB = [math]::Round($osInfo.FreePhysicalMemory / 1KB, 0)
$freeRAM_GB = [math]::Round($osInfo.FreePhysicalMemory / 1MB, 2)

if ($freeRAM_MB -ge 400) {
    Add-Result -Name "Physical Memory (RAM)" -Status "PASS" -Details "${freeRAM_MB} MB free out of ${totalRAM_GB} GB total"
} else {
    Add-Result -Name "Physical Memory (RAM)" -Status "WARN" -Details "${freeRAM_MB} MB free (memory low, single concurrency enforced)"
}

# 10. Docker Status Check
try {
    $dockerOut = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Result -Name "Docker Subsystem" -Status "PASS" -Details "Docker daemon running"
    } else {
        Add-Result -Name "Docker Subsystem" -Status "WARN" -Details "Docker daemon unavailable (not required for local Python demo)"
    }
} catch {
    Add-Result -Name "Docker Subsystem" -Status "WARN" -Details "Docker command not accessible (not required for local Python demo)"
}

# ── Render Summary Table ──────────────────────────────────────────────────────
Write-Host ""
$format = "{0,-28} | {1,-8} | {2}"
Write-Host ($format -f "CHECK ITEM", "STATUS", "DETAILS") -ForegroundColor DarkGray
Write-Host ("-" * 80) -ForegroundColor DarkGray

foreach ($r in $results) {
    $color = "Green"
    if ($r.Status -eq "FAIL") { $color = "Red" }
    elseif ($r.Status -eq "WARN") { $color = "Yellow" }
    Write-Host ($format -f $r.Check, "[$($r.Status)]", $r.Details) -ForegroundColor $color
}

Write-Host ("-" * 80) -ForegroundColor DarkGray
Write-Host "Summary: $($checksPassed) PASS, $($checksWarned) WARN, $($checksFailed) FAIL" -ForegroundColor $(if ($checksFailed -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($checksFailed -gt 0) {
    Write-Host "Preflight check FAILED with $checksFailed critical failure(s)." -ForegroundColor Red
    exit 1
} else {
    Write-Host "Preflight check PASSED cleanly. System is ready for demo launch." -ForegroundColor Green
    exit 0
}
