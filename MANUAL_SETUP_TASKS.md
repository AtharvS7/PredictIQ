# Manual Setup Tasks — PredictIQ v2.5.0

> These tasks **cannot be automated** and require a human to complete them in the GitHub web UI or third-party platforms. Complete them in order.

---

## 1. GitHub Branch Protection Rules

**Location:** https://github.com/AtharvS7/PredictIQ/settings/branches

### Protect `main` branch:
1. Click **"Add branch protection rule"**
2. Branch name pattern: `main`
3. ✅ Require a pull request before merging
   - ✅ Require approvals: **1**
   - ✅ Dismiss stale pull request approvals when new commits are pushed
4. ✅ Require status checks to pass before merging
   - Search and add these required checks:
     - `Backend — Tests`
     - `Frontend — Build`
     - `Security — Secret + code scan`
5. ✅ Require conversation resolution before merging
6. ✅ Do not allow bypassing the above settings
7. Click **"Create"**

### Protect `dev` branch:
1. Click **"Add another rule"**
2. Branch name pattern: `dev`
3. ✅ Require status checks to pass before merging
   - Add: `Backend — Lint`, `Frontend — Type check`
4. Click **"Create"**

---

## 2. GitHub Secrets Configuration

**Location:** https://github.com/AtharvS7/PredictIQ/settings/secrets/actions

Add these **Repository Secrets** (Actions → Secrets → New repository secret):

| Secret Name                  | Where to find it                       |
|------------------------------|----------------------------------------|
| `SUPABASE_URL`               | Supabase Dashboard → Settings → API   |
| `SUPABASE_ANON_KEY`          | Supabase Dashboard → Settings → API   |
| `SUPABASE_SERVICE_ROLE_KEY`  | Supabase Dashboard → Settings → API   |
| `JWT_SECRET_TEST`            | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

---

## 3. GitHub Environments (for CD pipelines)

**Location:** https://github.com/AtharvS7/PredictIQ/settings/environments

### Create `staging` environment:
1. Click **"New environment"** → Name: `staging`
2. No protection rules needed

### Create `production` environment:
1. Click **"New environment"** → Name: `production`
2. ✅ Required reviewers: Add `AtharvS7` (and optionally one teammate)
3. ✅ Wait timer: 5 minutes (gives time to cancel a bad deploy)
4. Add environment-specific secrets:
   - `RAILWAY_TOKEN_PRODUCTION`
   - `PRODUCTION_API_URL`
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

---

## 4. Update CODEOWNERS (Replace Placeholders)

**File:** `.github/CODEOWNERS`

Replace these placeholder usernames with your actual teammates' GitHub usernames:
- `@TeammateAGithub` → e.g. `@john-doe`
- `@TeammateBGithub` → e.g. `@jane-smith`
- `@TeammateCGithub` → e.g. `@bob-dev`
- `@TeammateDGithub` → e.g. `@alice-ml`

---

## 5. Install `slowapi` Dependency

Run on your local machine:
```bash
cd backend
pip install slowapi>=0.1.9
```

---

## 6. Create a `dev` Branch (if it doesn't exist)

```bash
git checkout main
git checkout -b dev
git push origin dev
```

The `cd-staging.yml` workflow triggers on pushes to `dev`.

---

## 7. Optional — Deployment Platform Setup

### Railway (Backend hosting):
1. Sign up at https://railway.app
2. Connect your GitHub repository
3. Create a service named `predictiq-backend-staging`
4. Set environment variables (same as `.env`)
5. Copy the Railway token to GitHub Secret: `RAILWAY_TOKEN_STAGING`

### Vercel (Frontend hosting):
1. Sign up at https://vercel.com
2. Import the `PredictIQ` repo → set root to `frontend/`
3. Copy `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` to GitHub Secrets

---

## 8. Bitwarden Setup (Credential Sharing)

1. Create a free Bitwarden organization at https://vault.bitwarden.com
2. Create a collection named "PredictIQ"
3. Add entries for:
   - Supabase URL
   - Supabase Anon Key
   - Supabase Service Role Key
   - JWT Secret
4. Share the collection with team members (read-only)

---

## Verification

After completing all steps, run this checklist:

```bash
# 1. Security scan should pass
python scripts/pre_push_check.py

# 2. Backend tests should pass
cd backend && python -m pytest tests/ -v

# 3. Frontend should build cleanly
cd frontend && npm run build

# 4. Push a test branch and verify CI runs
git checkout -b test/verify-ci
git push origin test/verify-ci
# Check GitHub Actions tab — all jobs should trigger
```

---

> **Once all steps above are complete, delete this file** — it's a temporary setup guide.
