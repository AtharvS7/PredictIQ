Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# GitHub Secrets & Environments Configuration Guide

This guide documents the configuration of GitHub Actions repository secrets, variables, and deployment environments required to power PredictIQ CI/CD pipelines.

---

## 1. GitHub Environments Architecture

PredictIQ utilizes GitHub Environments to enforce separation of duties, role-based deployment approvals, and environment-scoped credentials:

- **`staging`**: Automated deployment upon merge to `dev3`. Uses staging Neon database and staging Firebase project.
- **`production`**: Gated deployment upon release tag creation (`v*`). Requires mandatory review and sign-off by a designated release engineer.

---

## 2. Secrets & Variables Reference Matrix

### Backend Secrets (Configured under `Secrets`)

| Secret Name | Scope | Used By | Description |
|-------------|-------|---------|-------------|
| `DATABASE_URL` | Staging / Production | `ci.yml`, `cd-*.yml` | Neon PostgreSQL connection URI (`sslmode=require`). |
| `FIREBASE_CREDENTIALS_JSON` | Staging / Production | Backend runtime | Raw JSON string of the Firebase service account certificate. |
| `AWS_ACCESS_KEY_ID` | Staging / Production | ECR / ECS deployments | AWS IAM access key with deployment permissions. |
| `AWS_SECRET_ACCESS_KEY` | Staging / Production | ECR / ECS deployments | AWS IAM secret key. |
| `S3_ACCESS_KEY_ID` | Staging / Production | Backend storage | Scoped IAM key for document uploads bucket. |
| `S3_SECRET_ACCESS_KEY` | Staging / Production | Backend storage | Scoped IAM secret for document uploads bucket. |

---

### Frontend Variables (Configured under `Variables`)

Vite environment variables are public build artifacts compiled into the client bundle and should be configured as **Repository / Environment Variables**:

| Variable Name | Environment | Value Example |
|---------------|-------------|---------------|
| `VITE_API_BASE_URL` | Staging | `https://staging-api.predictiq.io/api/v1` |
| `VITE_API_BASE_URL` | Production | `https://api.predictiq.io/api/v1` |
| `VITE_FIREBASE_API_KEY` | Staging / Production | Web API Key from Firebase Console |
| `VITE_FIREBASE_AUTH_DOMAIN` | Staging / Production | `<project-id>.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | Staging / Production | `<project-id>` |
| `VITE_FIREBASE_STORAGE_BUCKET`| Staging / Production | `<project-id>.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID`| Staging / Production | Numeric sender ID |
| `VITE_FIREBASE_APP_ID` | Staging / Production | `1:1234567890:web:abcdef123456` |

---

## 3. Step-by-Step Configuration in GitHub UI

1. Go to repository on GitHub &rarr; **Settings** &rarr; **Environments**.
2. Click **"New environment"** and create:
   - `staging`
   - `production`
3. In the `production` environment:
   - Check **"Required reviewers"** and add senior release engineers.
   - Restrict deployment branches to **Selected branches** &rarr; `refs/tags/v*`.
4. Click **"Add secret"** in each environment to add environment-specific values for `DATABASE_URL` and `FIREBASE_CREDENTIALS_JSON`.
5. Under **Settings** &rarr; **Secrets and variables** &rarr; **Actions** &rarr; **Variables**, configure the global repository variables (`PYTHON_VERSION = "3.12"`, `NODE_VERSION = "22"`).

---

## 4. Local Development Mirroring

To replicate the CI/CD secret injection locally:
```bash
# Backend
cp backend/.env.example backend/.env
# Frontend
cp frontend/.env.example frontend/.env
```
Fill in the values from your development Neon and Firebase projects.

> [!CAUTION]
> Never commit `.env`, `*.pem`, or `serviceAccount*.json` files to Git. The unified release gate (`scripts/release_gate.py`) scans all commits for forbidden files and immediately aborts if any credential artifacts are detected.
