Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Running PredictIQ Locally on Windows 11

This specification outlines the procedure for running the PredictIQ application on a Windows workstation with Python 3.12, Node.js 22, and PowerShell.

---

## 1. System Requirements and Architecture

- **Operating System:** Windows 10/11 (64-bit)
- **Runtime Interpreters:** Python 3.12.x (`.venv`), Node.js v22+
- **Backend Framework:** FastAPI running on Uvicorn
- **Frontend Framework:** React 19 with Vite and TypeScript
- **Database:** PostgreSQL (Cloud instance via `DATABASE_URL` or local PostgreSQL instance)
- **Authentication:** Firebase Client SDK and Firebase Admin SDK

---

## 2. Directory Layout and Port Allocation

| Component | Default Working Path | Runtime Port | Protocol / Path |
|:----------|:---------------------|:------------:|:----------------|
| **FastAPI Backend** | `backend/` | `8010` (8010-8019) | HTTP / OpenAPI (`/docs`), Readiness (`/api/v1/ready`) |
| **Vite Frontend** | `frontend/` | `5173` | HTTP / Single Page Application |
| **PostgreSQL Database** | External Cloud or Local | `5432` | TCP / Asyncpg Connection Pool |

---

## 3. Step-by-Step Setup and Execution

### Step 1: Clone Repository and Enter Directory
```powershell
Set-Location E:\Codex\PredictIQ-dev3
```

### Step 2: System Preflight Verification
Execute the preflight script to audit interpreters, environment configuration, database reachability, and machine limits:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/preflight.ps1
```
Expected output:
```text
================================================================================
                      PREDICTIQ SYSTEM PREFLIGHT AUDIT                          
================================================================================
CHECK ITEM                   | STATUS   | DETAILS
--------------------------------------------------------------------------------
Python Interpreter           | [PASS]   | Python 3.12.2 (.venv)
Backend Environment          | [PASS]   | All required variables present: DATABASE_URL, FIREBASE_CREDENTIALS_PATH, APP_ENV
Database & Migrations        | [PASS]   | Host reachable (Alembic verified)
Firebase Configuration       | [PASS]   | Project ID matched (predictiq-a8bff)
Internet Connectivity        | [PASS]   | Outbound HTTPS connection verified (github.com:443)
ML Serving Runtime           | [PASS]   | Model loaded, p50=616.1 hrs for 50 FP
Port Availability            | [PASS]   | Backend demo port (8010) and Frontend (5173) are free
Disk Free Space              | [PASS]   | Adequate storage capacity verified
Physical Memory (RAM)        | [PASS]   | Sufficient physical memory detected
Docker Subsystem             | [PASS]   | Docker daemon running
--------------------------------------------------------------------------------
Summary: 10 PASS, 0 WARN, 0 FAIL
Preflight check PASSED cleanly. System is ready for demo launch.
```

### Step 3: Launch Demonstration Environment
Run the one-command launcher:
```powershell
python run.py
```
Alternatively, execute the PowerShell demo script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1
```
The launcher starts the FastAPI service on free ports (8010-8019), polls the `/api/v1/ready` readiness endpoint until healthy, launches the Vite frontend (5173-5179), and opens the application in your default browser.

Active endpoints:
- Application UI: `http://localhost:5173`
- Backend Documentation: `http://localhost:8010/docs`
- Health Probe: `http://localhost:8010/api/v1/ready`

### Step 4: Stop Demonstration Environment
When finished, press **Ctrl+C** in the terminal running `python run.py`, or execute the PowerShell cleanup script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop_demo.ps1
```

---

## 4. Quick Checks Reference Table

| Symptom / Condition | Diagnostic Command | Expected Resolution |
|:--------------------|:-------------------|:--------------------|
| **Port 8010 in use** | `netstat -ano \| findstr :8010` | Run `scripts/stop_demo.ps1` to release port, or check process ID. |
| **Database unreachable** | `Test-NetConnection -Port 5432` | Verify network connection and firewall permissions to the PostgreSQL host. |
| **Firebase uninitialized** | Inspect `backend/.env` | Ensure `FIREBASE_CREDENTIALS_PATH` points to a valid service account JSON file. |
| **Wrong Python Version** | `.\.venv\Scripts\python.exe --version` | Confirm path targets the Python 3.12 virtual environment rather than system PATH. |

---

## 5. Offline Demonstration Script
For an offline evaluation of model inference without starting network services:
```powershell
.\.venv\Scripts\python.exe scripts/demo_ml.py
```
This loads model parameters from JSON artifacts and evaluates standard project sizes directly.
