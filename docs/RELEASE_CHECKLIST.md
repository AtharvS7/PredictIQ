# Release Checklist — PredictIQ

Use this checklist for every release. Do not skip steps.

---

## Pre-Release (Developer)

- [ ] All features for this version merged to `dev`
- [ ] `python -m pytest backend/tests/ -v` passes with 0 failures
- [ ] `cd frontend && npm run build` succeeds with 0 TypeScript errors
- [ ] `python scripts/pre_push_check.py` passes with 0 issues
- [ ] `CHANGELOG.md` updated with all changes under new version header
- [ ] `APP_VERSION` in `backend/app/core/config.py` updated
- [ ] `docs/walkthrough.md` version number and changelog section updated
- [ ] `README.md` badge version updated if applicable

## Review (Second Team Member)

- [ ] PR from `dev` → `main` reviewed and approved
- [ ] All CI checks green (lint, tests, security-scan, build)
- [ ] Staging deployment verified manually (check `/api/v1/health`)
- [ ] One manual test of the full flow (upload SRS → see estimate)

## Release (Owner)

- [ ] PR merged to `main`
- [ ] Tag created: `git tag -a vX.Y.Z -m "PredictIQ vX.Y.Z — brief"`
- [ ] Tag pushed: `git push origin vX.Y.Z`
- [ ] CD pipeline completes successfully
- [ ] Production health check passes
- [ ] GitHub Release created automatically by `cd-production.yml`

## Post-Release

- [ ] Team notified in group chat
- [ ] If professor demo: test the production URL yourself before the demo
- [ ] Monitor production logs for 30 minutes after deployment
