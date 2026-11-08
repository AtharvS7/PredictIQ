Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Operational Runbook: Credential & Secret Rotation

This runbook provides actionable commands for rotating production secrets and database credentials across the PredictIQ operational stack.

---

## 1. Neon Database Credential Rotation

When rotating the PostgreSQL database password in Neon:

```bash
# 1. Using Neon CLI or Console, add secondary password for role 'predictiq'
# Note: Neon allows two concurrent active passwords for seamless rotation.

# 2. Update AWS Secrets Manager
aws secretsmanager update-secret \
  --secret-id "predictiq/production/database-url" \
  --secret-string "<NEON_ROTATED_CONNECTION_STRING_WITH_NEW_PASSWORD>"

# 3. Update GitHub Actions Staging & Production Secrets
gh secret set DATABASE_URL --env production --body "<NEON_ROTATED_CONNECTION_STRING_WITH_NEW_PASSWORD>"

# 4. Trigger rolling update on ECS Fargate
aws ecs update-service \
  --cluster predictiq-prod \
  --service predictiq-backend \
  --force-new-deployment

# 5. Verify /ready returns HTTP 200
curl -f https://api.predictiq.io/api/v1/ready

# 6. Delete the deprecated secondary password in Neon Console
```

---

## 2. Firebase Service Account Rotation

1. Go to **Firebase Console** &rarr; **Project Settings** &rarr; **Service accounts**.
2. Click **"Generate new private key"**.
3. Update AWS Secrets Manager:
   ```bash
   aws secretsmanager update-secret \
     --secret-id "predictiq/production/firebase-credentials" \
     --secret-string file://new-key.json
   ```
4. Update GitHub Actions secret `FIREBASE_CREDENTIALS_JSON`.
5. Trigger ECS container rolling deployment.
6. Verify authentication smoke test:
   ```bash
   python scripts/check_operations.py --base-url https://api.predictiq.io
   ```
7. In Google Cloud Console IAM, delete the old service account key ID.

---

## 3. Git History Cleansing (Accidental Secret Commit)

If a secret was committed to Git:

```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Excise secret file from entire repository history
git-filter-repo --path backend/.env --invert-paths

# 3. Force push updated history to all remotes
git push origin --force --all
git push origin --force --tags

# 4. Notify team: all team members must re-clone or rebase their local repositories
```
