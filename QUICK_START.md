# PredictIQ — Quick Start Guide

> Get PredictIQ running locally in under 5 minutes.

## Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 20+** — [Download](https://nodejs.org/)
- **Supabase Account** — [Sign up free](https://supabase.com/)

## Step 1: Clone the Repository

```bash
git clone https://github.com/AtharvS7/PredictIQ.git
cd PredictIQ
```

## Step 2: Configure Environment Variables

```bash
# Windows
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env

# macOS / Linux
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Open both `.env` files and fill in your Supabase credentials:

**`backend/.env`**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**`frontend/.env`**
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

> You can find these in your Supabase Dashboard → Settings → API.

## Step 3: Train the ML Model (One-Time)

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.lock.txt
cd backend
python -m ml.train
cd ..

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.lock.txt
cd backend
python -m ml.train
cd ..
```

This generates the model files (~10 seconds). Only needed once.

## Step 4: Run the App

```bash
python run.py
```

This will:
1. Create/verify the virtual environment
2. Install all Python + Node.js dependencies
3. Start the backend (FastAPI) on **http://localhost:8000**
4. Start the frontend (Vite) on **http://localhost:5173**

Open **http://localhost:5173** in your browser — you're ready to go!

## Other Commands

```bash
python run.py --backend     # Backend only
python run.py --frontend    # Frontend only
python run.py --install     # Install deps without starting servers
```

## Need Help?

- Full technical docs: [docs/walkthrough.md](docs/walkthrough.md)
- Security & CI setup: [docs/GITHUB_SECRETS_SETUP.md](docs/GITHUB_SECRETS_SETUP.md)
