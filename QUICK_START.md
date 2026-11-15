# PredictIQ — Quick Start Guide

> Effort and duration estimation for software engineering projects using empirical calibration.

---

## 1. Prerequisites

- **Python 3.12** — Installed in local virtual environment at `.venv`
- **Node.js 22+ & npm** — Required for Vite frontend execution
- **PostgreSQL Database** — Cloud connection via `DATABASE_URL` or local PostgreSQL instance
- **Firebase Project** — Configuration for web authentication and service account credentials

---

## 2. Fast Launch (Windows One-Command Demo)

To launch both the backend API and frontend application with automated health verification:

```powershell
# 1. Run environment preflight audit
powershell -ExecutionPolicy Bypass -File scripts/preflight.ps1

# 2. Start demo environment
powershell -ExecutionPolicy Bypass -File scripts/start_demo.ps1
```

Once running, access the services:
- **Frontend Application:** [http://localhost:5173](http://localhost:5173)
- **Interactive OpenAPI Documentation:** [http://localhost:8010/docs](http://localhost:8010/docs)
- **Service Readiness Probe:** [http://localhost:8010/api/v1/ready](http://localhost:8010/api/v1/ready)

To shut down demo services cleanly:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop_demo.ps1
```

---

## 3. Manual Step-by-Step Setup

### Step 1: Environment Variables Configuration

Copy example environment files to active configuration:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

Ensure the following settings are defined:

**`backend/.env`**
```ini
DATABASE_URL=postgresql://user:password@host:5432/database
FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
APP_ENV=development
```

**`frontend/.env`**
```ini
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_API_BASE_URL=http://localhost:8010/api/v1
```

### Step 2: Database Schema Verification

Verify that database migrations are aligned with application models:
```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic heads
Set-Location ..
```

### Step 3: Start Services Manually

**Terminal 1 — FastAPI Backend (Port 8010):**
```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8010
```

**Terminal 2 — Vite Frontend (Port 5173):**
```powershell
Set-Location frontend
npm run dev
```

---

## 4. Verification and Offline Testing

To test model inference without network or database dependencies:
```powershell
.\.venv\Scripts\python.exe scripts/demo_ml.py
```

To run test suites:
```powershell
# Backend pytest suite
.\.venv\Scripts\python.exe -m pytest backend/tests/ -q

# Frontend component suite
npm --prefix frontend test
```

For operational details and troubleshooting reference, see [RUN_LOCALLY_WINDOWS.md](docs/operations/RUN_LOCALLY_WINDOWS.md).
