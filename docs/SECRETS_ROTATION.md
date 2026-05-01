# Secrets Rotation Policy — Predictify

> **Effective:** May 2026 | **Review Cycle:** Quarterly | **Owner:** Platform Team

---

## 1. Rotation Schedule

| Secret | Location | Rotation Frequency | Last Rotated | Next Due |
|--------|----------|:------------------:|:------------:|:--------:|
| Firebase Service Account Key | `FIREBASE_SERVICE_ACCOUNT` env var | Every 90 days | — | — |
| Neon PostgreSQL DSN | `DATABASE_URL` env var | Every 90 days | — | — |
| GitHub Actions Secrets | Repository Settings → Secrets | Every 180 days | — | — |
| Railway Deploy Token | Railway dashboard | Every 180 days | — | — |
| JWT Signing Key (if custom) | `JWT_SECRET` env var | Every 90 days | — | — |

---

## 2. Rotation Procedure

### 2.1 Firebase Service Account

1. Go to [Firebase Console](https://console.firebase.google.com/) → Project Settings → Service Accounts
2. Click **Generate New Private Key**
3. Update the `FIREBASE_SERVICE_ACCOUNT` env var in Railway/deployment
4. Update the local `backend/firebase-service-account.json` (git-ignored)
5. Verify: `python backend/scripts/test_firebase.py`
6. Revoke the old key after 24-hour soak period

### 2.2 Neon PostgreSQL DSN

1. Go to [Neon Dashboard](https://console.neon.tech/) → Connection Details
2. Click **Reset Password** for the database role
3. Copy the new connection string
4. Update `DATABASE_URL` in Railway and `.env`
5. Verify: hit `/api/v1/health` and confirm `db_connected: true`

### 2.3 GitHub Actions Secrets

1. Go to GitHub → Repository → Settings → Secrets and Variables → Actions
2. Update each secret with the new value
3. Trigger a CI run on `dev` branch to verify

---

## 3. Emergency Rotation

If a secret is **suspected compromised**:

1. **Immediately** rotate the affected credential using the procedure above
2. Revoke the old credential (do NOT wait for soak period)
3. Audit recent access logs for unauthorized usage
4. Notify the team via the incident channel
5. Document the incident in `docs/incidents/`

---

## 4. Automation (Future)

- [ ] Set up GitHub Dependabot for secret scanning alerts
- [ ] Integrate HashiCorp Vault or AWS Secrets Manager for auto-rotation
- [ ] Add CI check that warns if secrets are older than 90 days

---

## 5. Compliance Notes

- **SOC 2 Type II** requires documented evidence of secret rotation
- Keep a log of rotation dates in this file or in a secure audit trail
- All secrets must be stored encrypted at rest (Railway and GitHub both provide this)
- Never commit secrets to version control — `.gitignore` and pre-commit hooks enforce this

---

> *Policy created May 1, 2026 — Predictify v3.1.6*
> *Next review: August 2026*
