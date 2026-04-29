# Predictify — GitHub Secrets Setup Guide

This guide explains how to configure GitHub repository secrets for CI/CD and deployment.

## Required Secrets

| Secret Name | Where to Find | Used By |
|-------------|--------------|---------|
| `SUPABASE_URL` | Supabase Dashboard → Settings → API → Project URL | Backend `.env` |
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API → `anon` `public` key | Frontend + Backend |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard → Settings → API → `service_role` key | Backend only (NEVER expose to frontend) |
| `VITE_SUPABASE_URL` | Same as `SUPABASE_URL` | Frontend `.env` |
| `VITE_SUPABASE_ANON_KEY` | Same as `SUPABASE_ANON_KEY` | Frontend `.env` |

## How to Add Secrets

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter the **Name** exactly as shown above
4. Paste the **Value** from your Supabase dashboard
5. Click **Add secret**

## Security Rules

- **NEVER** commit `.env` files to the repository
- **NEVER** use `service_role` key in frontend code
- **NEVER** log secret values in CI output
- **ALWAYS** use `${{ secrets.SECRET_NAME }}` in GitHub Actions workflows
- **ALWAYS** rotate keys if they are accidentally exposed

## Local Development

For local development, copy the example env files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Then fill in the values from your Supabase dashboard.

## CI/CD Integration

Secrets are automatically injected into the CI pipeline via the `ci.yml` workflow.
The `security-scan` job runs `scripts/pre_push_check.py` to verify no secrets
are hardcoded in the source code.
