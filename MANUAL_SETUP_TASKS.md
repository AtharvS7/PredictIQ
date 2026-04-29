# Manual Setup Tasks — Predictify v2.5.0

> These tasks **cannot be automated** and require a human to complete them in the GitHub web UI or third-party platforms. Complete them in order.

---

## 1. GitHub Branch Protection Rules

**Location:** https://github.com/AtharvS7/Predictify/settings/branches

> **Goal:** AtharvS7 (`@AtharvS7`) can push directly to `main` and `dev` without
> needing any approvals. Everyone else must create a PR and get approval before merging.

### Protect `main` branch:
1. Click **"Add branch protection rule"** (or edit existing rule)
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
6. ❌ **Do NOT check** "Do not allow bypassing the above settings" (leave this UNCHECKED)
7. Scroll down to **"Allow specified actors to bypass required pull requests"**
   - Click the search box and type `AtharvS7`
   - Select your account — it will appear as a user
   - This lets YOU push directly. Everyone else still needs a PR + approval.
8. Click **"Create"** (or **"Save changes"** if editing)

### Protect `dev` branch:
1. Click **"Add another rule"**
2. Branch name pattern: `dev`
3. ✅ Require status checks to pass before merging
   - Add: `Backend — Lint`, `Frontend — Type check`
4. ❌ **Do NOT check** "Do not allow bypassing the above settings"
5. Scroll down to **"Allow specified actors to bypass required pull requests"**
   - Add `AtharvS7` here too
6. Click **"Create"

---

## 2. GitHub Secrets Configuration

**Location:** https://github.com/AtharvS7/Predictify/settings/secrets/actions

Add these **Repository Secrets** (Actions → Secrets → New repository secret):

| Secret Name                  | Where to find it                       |
|------------------------------|----------------------------------------|
| `SUPABASE_URL`               | Supabase Dashboard → Settings → API   |
| `SUPABASE_ANON_KEY`          | Supabase Dashboard → Settings → API   |
| `SUPABASE_SERVICE_ROLE_KEY`  | Supabase Dashboard → Settings → API   |
| `JWT_SECRET_TEST`            | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

---

## 3. GitHub Environments (for CD pipelines)

**Location:** https://github.com/AtharvS7/Predictify/settings/environments

> ⚠️ **The CD pipelines (staging + production) will NOT run until you push to `dev`
> or create a version tag.** You can safely create empty environments now and add
> deployment secrets later when you're ready to deploy. The CI pipeline (testing,
> linting, security) works perfectly without any of these.

### ✅ Do NOW — Create empty environments:

**Create `staging` environment:**
1. Click **"New environment"** → Name: `staging`
2. No protection rules needed — leave everything blank

**Create `production` environment:**
1. Click **"New environment"** → Name: `production`
2. ✅ Required reviewers: Add `AtharvS7` (and optionally one teammate)
3. ✅ Wait timer: 5 minutes (gives time to cancel a bad deploy)
4. **Leave secrets empty for now**

### 🔜 Do LATER — When ready to deploy (add these secrets to the environments):

| Secret Name                  | Platform | How to get it |
|------------------------------|----------|---------------|
| `VERCEL_TOKEN`               | Vercel   | Settings → Tokens → Create Token |
| `VERCEL_ORG_ID`              | Vercel   | Settings → General → Your ID |
| `VERCEL_PROJECT_ID`          | Vercel   | Project → Settings → General → Project ID |
| `RAILWAY_TOKEN_STAGING`      | Railway  | Account → Tokens → Create Token |
| `RAILWAY_TOKEN_PRODUCTION`   | Railway  | Account → Tokens → Create Token |
| `PRODUCTION_API_URL`         | Railway  | Your deployed service URL (e.g. `https://Predictify-api.up.railway.app`) |
| `STAGING_API_URL`            | Railway  | Your staging service URL |

---

## 4. ~~Update CODEOWNERS~~ ✅ DONE

**File:** `.github/CODEOWNERS` — already updated with real usernames.

| Code Area | Owners |
|-----------|--------|
| Global fallback | `@AtharvS7` + `@RohiniJanardhanPhad` |
| Frontend (`frontend/src/`) | `@AtharvS7` + `@Shravani0605` + `@Shruti10101-1` |
| Backend (`backend/app/`) | `@AtharvS7` + `@RohiniJanardhanPhad` |
| ML Model (`backend/ml/`) | `@AtharvS7` + `@Shekhar2006` |
| CI/CD (`.github/`) | `@AtharvS7` + `@RohiniJanardhanPhad` |
| Documentation (`docs/`) | `@AtharvS7` + `@RohiniJanardhanPhad` |
| Database migrations | `@AtharvS7` only |

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
3. Create a service named `Predictify-backend-staging`
4. Set environment variables (same as `.env`)
5. Copy the Railway token to GitHub Secret: `RAILWAY_TOKEN_STAGING`

### Vercel (Frontend hosting):
1. Sign up at https://vercel.com
2. Import the `Predictify` repo → set root to `frontend/`
3. Copy `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` to GitHub Secrets

---

## 8. Bitwarden Setup (Credential Sharing)

1. Create a free Bitwarden organization at https://vault.bitwarden.com
2. Create a collection named "Predictify"
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

## 9. Fix: Allow AtharvS7 to Push Directly (If Already Blocked)

If you already created branch protection and now you're blocked from pushing:

1. Go to: https://github.com/AtharvS7/Predictify/settings/branches
2. Click **"Edit"** next to the `main` rule
3. Find **"Do not allow bypassing the above settings"** → **UNCHECK it**
4. Find **"Allow specified actors to bypass required pull requests"**:
   - Type `AtharvS7` in the search box
   - Select your account
5. Click **"Save changes"**
6. Repeat for the `dev` rule if it exists

**What this does:**
- ✅ `AtharvS7` → can `git push origin main` directly, no PR needed
- ❌ Everyone else → must create a PR → needs 1 approval → then merge

**Test it:** After saving, try pushing from your terminal:
```bash
git checkout main
git push origin main
```
If it works, you're set. If it still fails, double-check that "Do not allow bypassing" is **unchecked**.

---

> **Once all steps above are complete, delete this file** — it's a temporary setup guide.
