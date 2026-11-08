Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Team Member Onboarding & Access Provisioning Runbook

This runbook outlines the required steps to onboard new software engineers and data scientists to the PredictIQ repository and development environment.

---

## 1. Access Provisioning

### 1.1. GitHub Repository Access
1. Navigate to: `https://github.com/AtharvS7/PredictIQ/settings/collaborators`
2. Click **"Add people"** and enter the new member's GitHub handle.
3. Assign the **Write** role (Admin privileges are restricted to project maintainers).
4. Inform the engineer to accept the invitation link delivered to their registered email.

### 1.2. Cloud & Provider Access
- **Firebase Authentication**: Invite member to the development Firebase project with "Viewer" or "Firebase Authentication Admin" permissions.
- **Neon PostgreSQL**: Invite member to the Neon development workspace or provide a dedicated branch connection URI.
- **AWS Development Account**: Provide scoped IAM credentials restricted to development S3 bucket access.

---

## 2. Local Environment Setup

New members must configure their local workstation using Python 3.12 and Node.js 22:

```bash
# 1. Clone repository
git clone https://github.com/AtharvS7/PredictIQ.git
cd PredictIQ

# 2. Check out working branch
git checkout dev3

# 3. Configure backend environment
cp backend/.env.example backend/.env
# Populate DATABASE_URL with development Neon connection string
# Place development firebase-service-account.json in backend/

# 4. Configure frontend environment
cp frontend/.env.example frontend/.env
# Fill in development VITE_FIREBASE_* parameters

# 5. Install Python dependencies
py -3.12 -m venv backend/.venv
# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

pip install -r backend/requirements.lock.txt
pip install ruff mypy types-requests pytest pytest-asyncio pytest-cov httpx

# 6. Install frontend dependencies
npm --prefix frontend ci
```

---

## 3. Onboarding Verification Checklist

Verify local workstation readiness by running the unified release gate:

- [ ] GitHub invitation accepted and branch checked out (`dev3`).
- [ ] Dependencies cleanly installed (`backend` and `frontend`).
- [ ] `backend/.env` configured with development Neon connection string.
- [ ] Backend tests pass: `pytest backend/tests/test_health_ready.py -v`.
- [ ] Frontend tests pass: `npx --prefix frontend vitest run`.
- [ ] Release gate passes with skip-slow flag:
  ```bash
  python scripts/release_gate.py --skip-slow
  ```
- [ ] Understands Git workflow: branch off `dev3` &rarr; feature branch &rarr; pre-push release gate &rarr; pull request targeting `dev3`.
