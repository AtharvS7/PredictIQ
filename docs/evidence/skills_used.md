# Skills Used Registry

| Checkpoint | Skill (Path) | Why | What Changed Because of It | Helpful (Yes/No) |
|---|---|---|---|---|
| CP00 | `planner` (`.agents/skills/planner.md`) | CP00 baseline planning and step breakdown | Formulated 5-step execution plan for CP00 | Yes |
| CP00 | `code-explorer` (`.agents/skills/code-explorer.md`) | Exploring test suites and model hashes | Located artifacts and test modules quickly | Yes |
| CP00 | `opensource-sanitizer` (`.agents/skills/opensource-sanitizer.md`) | Reviewing working tree imports and untracked docs for secrets | Cleaned up .gitignore and verified no secrets committed | Yes |
| CP00 | `using-git-worktrees` (`.agents-disabled-20260908-103145/skills/using-git-worktrees/SKILL.md`) | Setting up isolated worktrees for workstreams | Configured `.worktrees/` directory and local workstream branches | Yes |
| CP01 | `architect` (`.agents/skills/architect.md`) | Defining system contracts, API v2 schema, and ML input boundaries | Established frozen ml_contract.md and api_estimate_v2.json | Yes |
| CP01 | `spec-miner` (`.agents/skills/spec-miner.md`) | Extracting behavioral assertions and invariants for evaluation | Structured frozen evaluation protocol and decision rule invariants | Yes |
| CP02 | `docs-lookup` (`.agents/skills/docs-lookup.md`) | Looking up software estimation datasets and licensing constraints | Verified license, unit, and URL definitions for 17 data sources | Yes |
| CP02 | `deep-research` (`.agents-disabled-20260908-103145/skills/deep-research/SKILL.md`) | Investigating recent academic software benchmarking datasets | Identified COSMIC Yürüm/Demirörs (2026) benchmark and ISBSG scope | Yes |
| CP03 | `python-reviewer` (`.agents/skills/python-reviewer.md`) | Reviewing data ingestion script for safe file parsing and type safety | Implemented named-column parsing, atomic writes, and China Effort assertion | Yes |
| CP04 | `mle-reviewer` (`.agents/skills/mle-reviewer.md`) | Reviewing feature schema harmonization and unit conversion integrity | Verified Albrecht thousand-hours rule and prohibited KLOC-to-FP conversions | Yes |
| CP05 | `tdd-guide` (`.agents/skills/tdd-guide.md`) | Designing automated data quality and leakage test suite | Created 9 comprehensive data property tests in test_data_v2.py | Yes |
| CP05 | `silent-failure-hunter` (`.agents/skills/silent-failure-hunter.md`) | Detecting subtle data parsing bugs and silent column misalignment | Uncovered AT&T whitespace column shift and corrected field mapping | Yes |
