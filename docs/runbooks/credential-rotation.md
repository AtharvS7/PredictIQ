# Emergency Credential Rotation Runbook

> **Trigger:** A secret was accidentally committed to git, shared insecurely, or potentially compromised.

---

## Step 1 — Immediately Invalidate the Exposed Credential

### If Supabase JWT Secret is exposed:
1. Go to: `https://supabase.com/dashboard/project/<project-id>/settings/api`
2. Click **"Regenerate JWT Secret"**
3. Copy the new JWT Secret
4. Update `backend/.env` on **ALL** developer machines
5. Update GitHub Secret: `JWT_SECRET` (both staging + production environments)
6. Redeploy both staging and production (trigger `cd-production.yml` manually)

### If Supabase Service Role Key is exposed:
1. Go to Supabase Dashboard → Settings → API
2. The service role key **cannot be rotated** in Supabase — you must:
   - a. Create a **NEW** Supabase project
   - b. Run all migration files from `supabase/migrations/` in the new project's SQL editor
   - c. Update **all** environment variables everywhere
   - d. This is a **major incident** — notify the team lead/professor

### If Railway or Vercel tokens are exposed:
1. Go to the respective platform's account settings
2. Revoke the exposed token
3. Generate a new token
4. Update the corresponding GitHub Secret

---

## Step 2 — Remove from Git History

```bash
# Install git-filter-repo (safer than git filter-branch)
pip install git-filter-repo

# Remove the file containing secrets from ALL history
git-filter-repo --path backend/.env --invert-paths

# Force push the cleaned history
git push origin --force --all --tags
```

> ⚠️ **Every team member must re-clone after this operation.**

---

## Step 3 — Verify Removal

```bash
# This must return EMPTY output
git log --all -p -- backend/.env
```

---

## Step 4 — Update All Developer Machines

Send message in group chat:
> **URGENT: Re-clone the repo and re-copy your `.env` from the shared credential vault.**

---

## Step 5 — Post-Incident

- [ ] Document what happened, when, and the timeline of response
- [ ] Verify all services are functional with new credentials
- [ ] Run `python scripts/pre_push_check.py` to confirm no secrets remain
- [ ] Consider adding a git pre-commit hook to prevent future incidents
