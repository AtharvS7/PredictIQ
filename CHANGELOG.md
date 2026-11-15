# Changelog

All notable features and capabilities of PredictIQ are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-11-15

### Added
- **Empirical Effort Estimation Runtime:** Zero-pickle serving engine utilizing a monotone power-law formulation ($a \cdot \text{Size}^b$) calibrated across 915 multi-source software projects.
- **Statistical Prediction Intervals:** Inductive conformal prediction providing 80% coverage intervals ($P_{10}$ to $P_{90}$) and 50% likely effort bands ($P_{25}$ to $P_{75}$) with stratified Mondrian calibration.
- **Organizational Calibration & Empirical Bayes Shrinkage:** Bayesian updating incorporating organization-specific project actuals via shrinkage weight $w = k / (k + 2.57)$, preserving locked national slope mechanics while tailoring scale to team velocity.
- **Multi-Format Software Requirements Specification (SRS) Parsing:** Robust document ingestion supporting DOCX, PDF, Markdown, plain text, and pasted requirements with structural heading, table, and list extraction.
- **Multi-Signal Natural Language Requirement Extraction:** Extraction pipeline analyzing user stories, numbered functional requirements, modal verb statements, use cases, and external integration points with source evidence tracking.
- **Interactive Web Interface:** Single-page application built on React 19, Vite, and TypeScript featuring estimation wizardry, parametric adjustment, interactive risk analyzers, and theme customization.
- **Comprehensive Project Budgeting:** Task and role-based budgeting subsystem calculating loaded personnel costs, hourly rate adjustments, and currency conversions across global rates.
- **Enterprise Authentication & Access Control:** Firebase Authentication integration featuring cryptographic JWT verification, session management, and granular role hierarchies.
- **Scenario Management & Export:** PDF and structured JSON estimate export, estimate duplication for comparative scenario planning, and password-protected external link sharing.
- **Automated Verification & Operational Tooling:** Preflight audit utilities, one-command demonstration management scripts, automated release verification, and offline model execution capabilities.
