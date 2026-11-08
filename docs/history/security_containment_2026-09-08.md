> [!WARNING]
> **Historical - superseded; do not use as guidance.** This document reflects an earlier development phase and is preserved solely for auditability.

Status: Historical | Applies to: Historical (superseded) | Verified against commit: cdca041 | Date: 2026-11-08

# Security containment follow-up

The migration helper now requires `DATABASE_URL` from the process environment and refuses missing or blank configuration before connecting. Connection and execution failures do not print database exception text, which can contain credentials or SQL values. No live migration was executed.

The source credential was removed. **Provider-side credential rotation remains required.** Removing the literal does not revoke existing credentials or remove historical copies. Rotation, connection invalidation, historical exposure review, and any published-history changes require the repository owner's provider access and coordination; these were not performed.

Docker builds exclude environment files, common service-account credential filenames, private keys, caches, and local uploads. Supply backend credentials through runtime secrets or `--env-file`. Keep credentials with arbitrary filenames outside the build context. Frontend public Firebase configuration is supplied through the six `VITE_FIREBASE_*` build arguments declared in `Dockerfile.frontend`, alongside `VITE_API_BASE_URL` and `VITE_APP_ENV`.

CI now uses Bandit's native high-severity exit status. Weekly Python auditing fails on vulnerabilities or scanner failures, and npm auditing fails on high/critical advisories or scanner failures. Reports upload even when a gate fails; the Node audit runs even if Python auditing fails. These gates may correctly block existing vulnerabilities until remediated.

Offline regression checks run with `python -m unittest discover -s scripts/tests -v`. Installing Bandit additionally exercises the real scanner against an intentionally unsafe temporary fixture.
