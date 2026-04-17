# Changelog

All notable changes to PredictIQ will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.5.0] — 2026-04-17

### Added
- Complete CI/CD pipeline: 7-stage CI (`ci.yml`) + staging (`cd-staging.yml`) + production (`cd-production.yml`)
- Weekly security audit workflow (`security-weekly.yml`) with automatic GitHub issue creation
- CodeQL SAST analysis for Python and JavaScript (`codeql.yml`)
- Dependabot auto-update PRs for pip, npm, and GitHub Actions (`dependabot.yml`)
- CODEOWNERS file for systematic code review assignments
- 3 operational runbooks: credential rotation, production deployment, team onboarding
- `pytest.ini` with coverage configuration and test markers
- `slowapi` rate limiting on estimation and health endpoints
- Startup validation for environment variables (Pydantic validators)
- Release checklist (`docs/RELEASE_CHECKLIST.md`)
- This CHANGELOG file

### Changed
- CI pipeline rewritten: added Ruff linting, mypy type checking, Bandit SAST, pytest-cov coverage
- `backend/app/core/config.py` now validates JWT_SECRET and SUPABASE_URL at startup
- `backend/main.py` now includes rate limiting middleware via slowapi
- APP_VERSION bumped to 2.5.0

### Security
- Added Bandit SAST scan to CI pipeline
- Added CodeQL weekly analysis for Python and JavaScript
- Added pip-audit and npm audit weekly dependency scanning
- Rate limiting prevents API abuse (10/min on estimates, 60/min on health)
- Startup crashes fast if credentials are placeholder values

## [2.4.0] — 2026-04-15

### Added
- NLP extractor v2.4: 4-strategy cascade architecture (Structural → Section-Aware → Global → Cross-Validation)
- `DocumentStructure` preprocessor for tables, headers, lists, sections
- `ExtractionResult` dataclass with per-field confidence + evidence
- 300+ keyword library across 7 technology categories
- 3 new NLP extractions: `integration_count`, `volatility_score`, `team_experience`
- 20-point complexity scoring system
- Pre-push security scanner (`scripts/pre_push_check.py`)
- `Makefile` for cross-platform developer convenience
- GitHub Secrets setup guide (`docs/GITHUB_SECRETS_SETUP.md`)
- Audit report with industry comparison (`docs/audit_report.md`)
- AGENTS.md, CLAUDE.md, GEMINI.md for AI-assisted development
- Knowledge graph tooling (code-review-graph)

### Changed
- NLP extractor rewritten from 539 to 900 lines
- NLP test suite expanded from 15 to 35 tests (total backend: 111)
- `estimates.py` wires 3 new NLP fields through the estimation pipeline
- `ml_service.py` uses `volatility_score` for T08, `team_experience` for TeamExp/ManagerExp
- CI pipeline updated: added security-scan job, Python 3.11 → 3.13
- `.gitignore` hardened with 15+ new patterns (46 total)
- `docs/walkthrough.md` completely rewritten (740 lines, 7 Mermaid diagrams)

### Fixed
- Removed hardcoded Supabase URL and anon key from `frontend/src/lib/supabase.ts` (CRITICAL)

## [2.3.0] — 2026-04-11

### Added
- Multi-currency support (10 currencies with real-time exchange rates)
- PDF, Excel, CSV export functionality
- Dark mode with glassmorphism UI design
- One-command launcher (`run.py`)
- Share links with optional password protection

### Changed
- Frontend redesigned with modern glassmorphism aesthetic
- Landing page with animated statistics and feature cards

## [2.0.0] — 2026-04-09

### Added
- Initial full-stack application
- Document upload (PDF/DOCX/TXT) with Supabase Storage
- NLP parameter extraction (8 fields, basic regex)
- XGBoost ML prediction (R² = 0.82, 740-record dataset)
- IFPUG function point estimation
- PERT-style min/likely/max predictions
- 10-factor risk analysis engine
- Supabase Auth (email/password JWT)
- React + TypeScript frontend with 3-step estimation wizard
- FastAPI backend with structured logging
- Docker support (Dockerfile.backend + Dockerfile.frontend)
- GitHub Actions CI pipeline
