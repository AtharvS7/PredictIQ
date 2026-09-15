# Release Checklist — Predictify

## Current release policy — September 15, 2026

This section supersedes the historical checklist below. The authorized source branch is **dev2 only**. Do not push main, other branches or tags. Hosting targets and access are pending; no deployment has occurred. See [deployment inputs](runbooks/DEPLOYMENT_INPUTS.md).

- [ ] Select hosting projects, budget, region and frontend/API URLs.
- [ ] Resolve the owner's ML execution hold; obtain compatible licensed data and independently approve a model.
- [ ] Install provider secrets and pass offline preflight, then verify actual access separately.
- [ ] Pass tests, build, type/lint and security checks on the exact release commit.
- [ ] Back up database and objects before additive migrations through `005_role_retry`.
- [ ] Deploy staging with readiness checks; verify real-provider estimation with the approved model and cross-user denial.
- [ ] Verify SPA deep links, HTTPS/CORS, private uploads and persistence across restart.
- [ ] Rehearse populated database/object restoration and rollback; record recovery targets.
- [ ] Configure resource limits, monitoring, alerts and retention; verify load behavior.
- [ ] Promote the same reviewed commit/artifact hashes and record production acceptance evidence.

The old tag-triggered production and `dev` staging workflows below are historical, not the current authorized deployment procedure. Keep provider auto-deploy disabled until the release path and ML execution hold are resolved.

## Historical checklist (superseded)

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
- [ ] Tag created: `git tag -a vX.Y.Z -m "Predictify vX.Y.Z — brief"`
- [ ] Tag pushed: `git push origin vX.Y.Z`
- [ ] CD pipeline completes successfully
- [ ] Production health check passes
- [ ] GitHub Release created automatically by `cd-production.yml`

## Post-Release

- [ ] Team notified in group chat
- [ ] If professor demo: test the production URL yourself before the demo
- [ ] Monitor production logs for 30 minutes after deployment
