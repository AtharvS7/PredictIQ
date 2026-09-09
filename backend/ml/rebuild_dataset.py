"""Reconstruct research data by named source columns; never modify legacy data.

One row is one completed project. Hours are observed person-hours, not resource
codes, elapsed duration, or inferred story points. Source size measurements may
differ, so cross-source validation is required before any production use.
"""
import csv
import hashlib
import io
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE_URL = "https://raw.githubusercontent.com/Derek-Jones/Software-estimation-datasets/main/"
SOURCES = {
    "china": ("china.arff", "ID", "AFP", "Effort"),
    "desharnais": ("Desharnais.csv", "Project", "PointsAjust", "Effort"),
    "maxwell": ("maxwell.arff", None, "Size", "Effort"),
    "kitchenham": ("kitchenham.arff", "Project", "Adjusted.function.points", "Actual.effort"),
}


def read_source(path: Path) -> pd.DataFrame:
    """Read these dense ARFF files without positional field assumptions."""
    if path.suffix == ".csv":
        return pd.read_csv(path)
    attributes, records = [], []
    in_data = False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("%"):
            continue
        if line.lower() == "@data":
            in_data = True
        elif in_data:
            records.append(line)
        elif line.lower().startswith("@attribute"):
            match = re.match(r"@attribute\s+(?:'([^']+)'|\"([^\"]+)\"|(\S+))\s+", line, re.IGNORECASE)
            if match is None:
                raise ValueError(f"Invalid attribute in {path.name}")
            attributes.append(next(value for value in match.groups() if value is not None).strip())
    if not attributes or not in_data or len(set(attributes)) != len(attributes):
        raise ValueError(f"Invalid schema in {path.name}")
    rows = list(csv.reader(io.StringIO("\n".join(records))))
    if any(len(row) != len(attributes) for row in rows):
        raise ValueError(f"Record width differs from schema in {path.name}")
    return pd.DataFrame(rows, columns=attributes).replace("?", np.nan)


def reconstruct(directory: Path) -> tuple[pd.DataFrame, dict]:
    frames, provenance = [], {}
    for source, (filename, id_column, size_column, effort_column) in SOURCES.items():
        path = directory / filename
        raw = read_source(path)
        frame = pd.DataFrame({
            "source": source,
            "project_id": raw[id_column].astype(str) if id_column else raw.index.astype(str),
            "size_fp": pd.to_numeric(raw[size_column], errors="raise"),
            "effort_hours": pd.to_numeric(raw[effort_column], errors="raise"),
        })
        if frame.project_id.duplicated().any():
            raise ValueError(f"Duplicate project identifiers in {source}")
        valid = np.isfinite(frame[["size_fp", "effort_hours"]]).all(axis=1)
        valid &= (frame[["size_fp", "effort_hours"]] > 0).all(axis=1)
        provenance[source] = {
            "url": SOURCE_URL + filename,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "raw_rows": len(raw), "usable_rows": int(valid.sum()),
            "excluded_missing_or_nonpositive": int((~valid).sum()),
            "size_column": size_column, "target_column": effort_column,
            "target_unit": "person-hours",
            "license_status": "not cleared for production or redistribution",
        }
        frames.append(frame.loc[valid].copy())
    data = pd.concat(frames, ignore_index=True)
    # Identical observable size/effort pairs stay in one split, even across sources.
    data["duplicate_group"] = [hashlib.sha256(f"{s:.12g}:{e:.12g}".encode()).hexdigest()[:20]
                               for s, e in zip(data.size_fp, data.effort_hours, strict=True)]
    return data, provenance


def audit_legacy(legacy: pd.DataFrame, china: pd.DataFrame) -> dict:
    source = china.apply(pd.to_numeric, errors="raise")
    lookup = {}
    for _, row in source.iterrows():
        key = (row.AFP, row.Input + row.Output + row.Enquiry, row.File + row.Interface)
        lookup.setdefault(key, []).append(row)
    wrong, examples = [], []
    for index, row in legacy.iterrows():
        matches = lookup.get((row.size_fp, row.Transactions, row.Entities), [])
        bad = [r for r in matches if row.effort_hours == r.Resource and r.Effort != r.Resource]
        if bad:
            wrong.append(int(index))
            if len(examples) < 5:
                examples.append({"legacy_row_zero_based": int(index), "china_id": int(bad[0].ID),
                                 "stored_hours": float(row.effort_hours),
                                 "source_hours": float(bad[0].Effort)})
    return {"rows": len(legacy), "resource_codes_used_as_hours": len(wrong),
            "affected_rows_zero_based": wrong, "examples": examples,
            "rows_at_9586_75": int(np.isclose(legacy.effort_hours, 9586.75).sum()),
            "status": "invalid_training_labels" if wrong else "requires_review"}


def main() -> None:
    output = ROOT / "experiments" / "reconstructed-v1"
    output.mkdir(parents=True, exist_ok=True)
    data, provenance = reconstruct(ROOT / "data" / "research")
    data.to_csv(output / "projects.csv", index=False)
    audit = audit_legacy(pd.read_csv(ROOT / "predictiq_merged_dataset.csv"),
                         read_source(ROOT / "data" / "research" / "china.arff"))
    report = {"sources": provenance, "total_usable_rows": len(data), "legacy_audit": audit,
              "production_approved": False,
              "exclusions": ["Finnish: size-method compatibility unverified",
                             "Huijgens: only 22 observed effort labels; rights pending",
                             "NASA: KLOC and person-months cannot be silently mapped to FP/hours"]}
    (output / "data_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(data), "sources": provenance,
                      "wrong_legacy_labels": audit["resource_codes_used_as_hours"]}, indent=2))


if __name__ == "__main__":
    main()
