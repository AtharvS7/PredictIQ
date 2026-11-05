"""Generate a truthful, reproducible inventory of PredictIQ ML research data.

This script reports research evidence only. It deliberately separates completed
project records from task-level data and never labels a research collection as a
production-approved training dataset.

Run from backend: python -m ml.dataset_status [--json OUTPUT.json]
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from ml.expanded_research import exclude_pairs, read_albrecht
from ml.external_validation import read_att
from ml.rebuild_dataset import reconstruct


ROOT = Path(__file__).resolve().parent


def inventory(research_directory: Path | None = None) -> dict:
    """Return source counts and release status derived from local source files."""
    research = research_directory or ROOT / "data" / "research"
    core, provenance = reconstruct(research)
    att = read_att(research / "aptness.dat.txt")
    observed_pairs = set(zip(core.size_fp, core.effort_hours, strict=True))
    att_overlap = att.apply(lambda row: (row.size_fp, row.effort_hours) in observed_pairs, axis=1)
    expanded = pd.concat([core, att.loc[~att_overlap]], ignore_index=True)
    albrecht = exclude_pairs(read_albrecht(research / "albrecht.arff"), expanded)

    return {
        "legacy": {
            "rows": 740,
            "source_identity_retained": False,
            "production_approved": False,
            "status": "revoked_corrupted_labels",
            "why": "481 effort labels used a resource category; 108 labels were capped",
        },
        "verified_core": {
            "rows": len(core),
            "sources": {name: values["usable_rows"] for name, values in provenance.items()},
            "grain": "completed_project",
            "target": "observed_person_hours",
            "production_approved": False,
        },
        "expanded_development": {
            "rows": len(expanded),
            "added_source": "AT&T Matson",
            "added_rows": int((~att_overlap).sum()),
            "excluded_possible_overlap": int(att_overlap.sum()),
            "grain": "completed_project",
            "production_approved": False,
        },
        "external_diagnostic": {
            "rows": len(albrecht),
            "source": "Albrecht",
            "purpose": "held-out diagnostic only; not reused for tuning",
            "production_approved": False,
        },
        "research_collection_rows": len(expanded) + len(albrecht),
        "production_ml_status": {
            "approved": False,
            "reason": "The collection lacks compatible planning-time evidence for the nine-feature production contract and has not passed independent external validation.",
            "required_next_step": "Acquire >=1000 licensed, modern completed projects with verified planning-time features and observed person-hours.",
        },
    }


def markdown(report: dict) -> str:
    core = report["verified_core"]
    expanded = report["expanded_development"]
    external = report["external_diagnostic"]
    source_rows = ", ".join(f"{name}: {rows}" for name, rows in core["sources"].items())
    return "\n".join([
        "# PredictIQ ML data status",
        "",
        f"- Legacy dataset: {report['legacy']['rows']} rows, revoked ({report['legacy']['why']}).",
        f"- Verified core: {core['rows']} completed projects across four named sources ({source_rows}).",
        f"- Expanded development collection: {expanded['rows']} projects after adding {expanded['added_rows']} AT&T projects; {expanded['excluded_possible_overlap']} possible overlaps excluded.",
        f"- External diagnostic: {external['rows']} Albrecht projects, held out from development tuning.",
        f"- Total research records: {report['research_collection_rows']} across six sources.",
        "",
        "This is a research inventory, not a production-approval claim.",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="Optional new JSON report path")
    parser.add_argument("--markdown", type=Path, help="Optional new Markdown report path")
    args = parser.parse_args()
    report = inventory()
    if args.json:
        if args.json.exists():
            raise ValueError("Refusing to overwrite an existing JSON report")
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.markdown:
        if args.markdown.exists():
            raise ValueError("Refusing to overwrite an existing Markdown report")
        args.markdown.write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
