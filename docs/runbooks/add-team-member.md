# Adding a New Team Member — Runbook

> **Who can do this:** Any team member with GitHub write access. Only Atharv can grant Admin access.

---

## Step 1 — GitHub Repository Access

1. Go to: `https://github.com/AtharvS7/PredictIQ/settings/collaborators`
2. Click **"Add people"**
3. Enter their GitHub username
4. Set role to **Write** (not Admin)
5. They will receive an email invitation to accept

---

## Step 2 — Credential Sharing

1. Share the Bitwarden collection with the new member (read-only unless they need admin)
2. They create their own `.env` files using values from the vault:
   - `backend/.env` from `backend/.env.example`
   - `frontend/.env` from `frontend/.env.example`
3. **Never send credentials in plain text** (no WhatsApp, Telegram, email, or Discord)

---

## Step 3 — Local Setup

Have the new member follow the [QUICK_START.md](../../QUICK_START.md) guide, then verify:

```bash
# Clone
git clone https://github.com/AtharvS7/PredictIQ.git
cd PredictIQ

# Setup environment
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
# Fill in credentials from Bitwarden vault

# Install and run
python run.py
```

---

## Step 4 — Onboarding Checklist

- [ ] GitHub invitation accepted
- [ ] Repo cloned successfully
- [ ] `venv` created and backend dependencies installed
- [ ] `backend/.env` configured with real Supabase credentials
- [ ] `frontend/.env` configured with real Supabase credentials
- [ ] ML model trained: `cd backend && python -m ml.train`
- [ ] Backend starts without errors (`python run.py --backend`)
- [ ] Frontend starts without errors (`python run.py --frontend`)
- [ ] All tests pass locally: `cd backend && python -m pytest tests/ -v`
- [ ] They have created a test branch and pushed it successfully
- [ ] They understand the PR workflow (branch → PR → review → merge)

---

## Step 5 — Update CODEOWNERS (if needed)

If the new member will own a specific area of code, update `.github/CODEOWNERS`:

```
# Example: adding @NewMember as frontend co-owner
frontend/src/             @TeammateAGithub @NewMemberGithub
```

---

## Team Communication

- Add them to the project group chat
- Share links to:
  - [Technical Walkthrough](../../docs/walkthrough.md)
  - [Release Checklist](../../docs/RELEASE_CHECKLIST.md)
  - [GitHub Secrets Setup](../../docs/GITHUB_SECRETS_SETUP.md)
