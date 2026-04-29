# Production Deployment Runbook

> **Who can do this:** Atharv + Teammate C (both have required credentials and GitHub access).

---

## Prerequisites

Before starting a production deployment, verify:

- [ ] All features for this release are merged to `dev`
- [ ] `python -m pytest backend/tests/ -v` returns 0 failures
- [ ] `cd frontend && npm run build` succeeds with 0 TypeScript errors
- [ ] `python scripts/pre_push_check.py` passes all checks
- [ ] The CI pipeline on `dev` branch is fully green

---

## Steps

### 1. Update version numbers
```bash
# Update backend version
# File: backend/app/core/config.py → APP_VERSION = "2.X.0"
```

### 2. Update CHANGELOG.md
Add a new section at the top of `CHANGELOG.md` following the Keep a Changelog format.

### 3. Commit and push
```bash
git add .
git commit -m "release: v2.X.0"
git push origin dev
```

### 4. Create Pull Request
- Open PR on GitHub: `dev` → `main`
- Title: `Release: v2.X.0`
- Description: Copy the CHANGELOG entry for this version

### 5. Wait for CI
- All CI checks must be green (backend-tests, frontend-build, security-scan)
- Get approval from at least **ONE** other team member

### 6. Merge the PR
- Use **squash merge** to keep main history clean

### 7. Tag the release
```bash
git checkout main
git pull origin main
git tag -a v2.X.0 -m "Predictify v2.X.0 — brief summary of changes"
git push origin v2.X.0
```

### 8. Verify deployment
- The `cd-production.yml` pipeline starts automatically on tag push
- Wait ~5 minutes for Railway + Vercel deployments
- Verify at: `<PRODUCTION_API_URL>/api/v1/health`
- Check the frontend loads correctly at the Vercel production URL

### 9. Announce
- Post in team group chat: `v2.X.0 is live ✅`

---

## If Deployment Fails

1. **Do NOT panic** — the old version is still running (Railway keeps it)
2. Check the GitHub Actions log for the failing step
3. If the smoke test fails, the old deployment remains active
4. Fix the issue on a `hotfix/fix-deploy` branch
5. Merge hotfix to main and re-tag:
   ```bash
   git tag -a v2.X.1 -m "hotfix: fix deployment issue"
   git push origin v2.X.1
   ```

---

## Rollback (if production is broken)

```bash
# Railway keeps previous deployments — roll back via dashboard:
# railway.app → Project → Deployments → Click previous successful deployment → Rollback

# For Vercel:
# vercel.com → Project → Deployments → Click "..." on previous → Promote to Production
```
