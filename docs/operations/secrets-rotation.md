Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Secrets, Database Credentials & API Key Rotation Procedures

This runbook specifies the step-by-step procedures for routine and emergency rotation of production secrets, database credentials, Firebase service account keys, and cloud storage tokens in PredictIQ.

---

## 1. Secrets Inventory & Routine Rotation Schedules

| Secret Identifier | Storage Location | Scope / Usage | Routine Frequency | Emergency Trigger |
|-------------------|------------------|---------------|-------------------|-------------------|
| **Neon PostgreSQL Password** | AWS Secrets Manager / GitHub Secrets | Backend database access | Every 90 days | Accidental commit / leaked log |
| **Firebase Service Account** | AWS Secrets Manager (`FIREBASE_CREDENTIALS_JSON`) | Backend token verification | Every 180 days | Compromised GCP project / credential leak |
| **AWS S3 / IAM Access Keys** | AWS Secrets Manager / IAM | Document storage read/write | Every 90 days | Compromised AWS access key |
| **JWT Signing Secret** | AWS Secrets Manager | Internal share token signing | Every 180 days | Token forgery / key leakage |

---

## 2. Step-by-Step Rotation Runbooks

### 2.1. Neon PostgreSQL Database Password Rotation (Zero Downtime)

Neon supports multiple concurrent passwords per database role to enable zero-downtime rotation:

```mermaid
sequenceDiagram
    autonumber
    actor Ops as Release Engineer
    participant Neon as Neon Cloud API / Console
    participant SM as AWS Secrets Manager
    participant App as PredictIQ ECS Fargate Tasks

    Ops->>Neon: Generate secondary password for role 'predictiq'
    Neon-->>Ops: New password generated (both old & new valid)
    Ops->>SM: Update secret 'predictiq/production/database-url'
    Ops->>App: Force new deployment (rolling update)
    Note over App: New containers boot with new password;<br/>old containers complete requests on old password
    App-->>Ops: All tasks healthy (/ready returns 200)
    Ops->>Neon: Delete old primary password
```

1. **Generate Secondary Password**:
   In the Neon Console &rarr; **Project Settings** &rarr; **Roles**, select role `predictiq` and click **"Add password"**. Both passwords are now concurrently active.
2. **Update AWS Secrets Manager**:
   ```bash
   aws secretsmanager update-secret \
     --secret-id "predictiq/production/database-url" \
     --secret-string "<NEON_ROTATED_CONNECTION_STRING_WITH_NEW_PASSWORD>"
   ```
3. **Execute Rolling Service Update**:
   ```bash
   aws ecs update-service \
     --cluster predictiq-prod \
     --service predictiq-backend \
     --force-new-deployment
   ```
4. **Verify Health**: Confirm `/api/v1/ready` returns HTTP 200 across all active tasks.
5. **Revoke Old Password**: In Neon Console, delete the deprecated password.

---

### 2.2. Firebase Service Account Key Rotation

Firebase Admin SDK private keys are managed within Google Cloud Platform:

1. **Create New Key**:
   - Navigate to **Firebase Console** &rarr; **Project Settings** &rarr; **Service accounts**.
   - Click **"Generate new private key"** and download the resulting JSON file.
2. **Update AWS Secrets Manager**:
   ```bash
   aws secretsmanager update-secret \
     --secret-id "predictiq/production/firebase-credentials" \
     --secret-string file://new-firebase-service-account.json
   ```
3. **Update Staging / GitHub Repository Secrets**:
   Update `FIREBASE_CREDENTIALS_JSON` in GitHub Actions repository secrets for staging and production environments.
4. **Redeploy Backend Containers**:
   Execute rolling update on ECS Fargate.
5. **Verify Authentication**:
   Execute `scripts/check_operations.py` and run a smoke test estimate to ensure ID token verification succeeds.
6. **Delete Expired Key**:
   In GCP Cloud Console &rarr; **IAM & Admin** &rarr; **Service Accounts**, delete the old key ID.

---

### 2.3. AWS IAM S3 Access Keys Rotation

Where IAM roles cannot be used (e.g. cross-account S3 or local CLI):

1. **Create Secondary Access Key**:
   ```bash
   aws iam create-access-key --user-name predictiq-s3-uploader
   # Save the AccessKeyId and SecretAccessKey
   ```
2. **Update Secrets Manager & Environment Variables**:
   Update `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`.
3. **Redeploy Services**:
   Restart backend tasks.
4. **Test Document Uploads**:
   Upload a test document to ensure S3 `PutObject` succeeds.
5. **Deactivate and Delete Old Key**:
   ```bash
   aws iam update-access-key --user-name predictiq-s3-uploader --access-key-id <OLD_KEY_ID> --status Inactive
   # After 24-hour verification window:
   aws iam delete-access-key --user-name predictiq-s3-uploader --access-key-id <OLD_KEY_ID>
   ```

---

## 3. Emergency Secret Revocation Protocol

If any production credential is confirmed leaked or compromised:

1. **Declare Incident**: Trigger Emergency Action Playbook A in `docs/security/incident-response.md`.
2. **Immediate Override**: Generate a replacement secret and update AWS Secrets Manager immediately.
3. **Terminate Active Connections**:
   ```sql
   -- Force terminate any active connections using compromised credentials
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE usename = 'predictiq' AND pid <> pg_backend_pid();
   ```
4. **Purge Git History**: If committed to Git, execute `git-filter-repo` and force push across all remotes.
5. **Review Audit Logs**: Trace all requests associated with the compromised credentials.
