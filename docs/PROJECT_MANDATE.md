# PredictIQ engineering mandate

User authorization, updated September 9, 2026.

The user authorizes autonomous engineering across the entire project: UI/UX redesign, backend architecture and logic, security hardening, database and API improvements, dataset replacement or expansion, model training and evaluation, testing, and documentation. Make substantive improvements when justified by implementation evidence; do not restrict work to cosmetic fixes or the original audit alone.

The intended outcome is a polished, credible, resume-worthy project with excellent usability, reliable estimation, maintainable implementation, clear documentation and diagrams, and strong security. Treat perfection as an aspiration, not an unverified completion claim.

## Working boundaries

- Proceed with ordinary investigation, edits, refactoring, tests, and local verification without repeatedly requesting permission.
- Preserve unrelated user work. Inspect implementation and reproduce defects before fixing them.
- Push authorized backups only to `dev2` at `https://github.com/AtharvS7/PredictIQ.git`. Do not push to `main`, other branches, or tags. Do not deploy without a deployment instruction.
- Keep credentials, environment files, generated reports, caches, local agent installations, and unapproved datasets/artifacts out of Git. Credential rotation is user-managed before deployment.
- Dataset access requiring payment, credentials, or unresolved usage rights still needs resolution. Do not fabricate observations or merge incompatible targets merely to increase row counts.
- Evaluate prediction improvements on independent data with explicit feature definitions, source provenance, leakage controls, uncertainty, and honest metrics. Do not claim a general accuracy or completion percentage without a defensible measurement.
- Maintain the walkthrough and diagrams alongside meaningful architectural changes. Record completed validation and remaining release gates.

## Current order of work

UI acceptance → configuration verification → populated recovery rehearsal → authenticated E2E → authorization and parser reliability → production ML validation and integration. Newly verified critical defects can take priority over this order.

This mandate records the user's project scope. It does not replace `AGENTS.md` or remove the need to protect secrets and preserve unrelated work.
