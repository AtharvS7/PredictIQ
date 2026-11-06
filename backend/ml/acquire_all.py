"""Idempotent dataset acquisition and checksum verification for PredictIQ v2.

Acquires and verifies all primary software estimation datasets with SHA-256 checks.
Parses files by named columns only and rigorously validates that China effort equals
source Effort person-hours, never the legacy resource code.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import tempfile
from pathlib import Path
from typing import NamedTuple
from urllib.request import Request, urlopen

import pandas as pd

ROOT_DATA_DIR = Path(__file__).resolve().parent / "data" / "research"


class SourceSpec(NamedTuple):
    name: str
    filename: str
    url: str
    expected_sha256: str
    size_field: str
    effort_field: str
    id_field: str | None


SOURCES: list[SourceSpec] = [
    SourceSpec(
        name="China",
        filename="china.arff",
        url="https://raw.githubusercontent.com/Derek-Jones/Software-estimation-datasets/main/china.arff",
        expected_sha256="ae9df9c52c5bc5ba03b9732ecc159093f0c500ffa0f3d8260ddd7350f0a22c58",
        size_field="AFP",
        effort_field="Effort",
        id_field="ID",
    ),
    SourceSpec(
        name="Kitchenham",
        filename="kitchenham.arff",
        url="https://raw.githubusercontent.com/Derek-Jones/Software-estimation-datasets/main/kitchenham.arff",
        expected_sha256="0832342b248418cca324cebe77d86d2f90ae223c1119af9360783bdbad0b2ac0",
        size_field="Adjusted.function.points",
        effort_field="Actual.effort",
        id_field="Project",
    ),
    SourceSpec(
        name="Desharnais",
        filename="Desharnais.csv",
        url="https://raw.githubusercontent.com/Derek-Jones/Software-estimation-datasets/main/Desharnais.csv",
        expected_sha256="38c5d00053555cbe7f3c10c2b026990ea981612ddefd5a7e0fcf8aa52bc4fd64",
        size_field="PointsAjust",
        effort_field="Effort",
        id_field="Project",
    ),
    SourceSpec(
        name="Maxwell",
        filename="maxwell.arff",
        url="https://raw.githubusercontent.com/Derek-Jones/Software-estimation-datasets/main/maxwell.arff",
        expected_sha256="1adb2b23c638a553a2b2e2d83476d983d1be13d4e891c4148f2a90834472c235",
        size_field="Size",
        effort_field="Effort",
        id_field=None,
    ),
    SourceSpec(
        name="Albrecht",
        filename="albrecht.arff",
        url="https://raw.githubusercontent.com/Derek-Jones/Software-estimation-datasets/main/albrecht.arff",
        expected_sha256="cfd9713c6a0a45e318fd5345d3f45ac1cfbbf59191d91a645eabd6541890fd18",
        size_field="AdjFP",
        effort_field="Effort",
        id_field=None,
    ),
    SourceSpec(
        name="AT&T Aptness",
        filename="aptness.dat.txt",
        url="https://jse.amstat.org/datasets/aptness.dat.txt",
        expected_sha256="92f4495226b89a26d5b1422e679445a4078bcca9905f08354988f796e3fcf210",
        size_field="size_fp",
        effort_field="effort_hours",
        id_field="id",
    ),
]


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 digest of a local file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def download_file(url: str, dest_path: Path, expected_sha256: str) -> None:
    """Download a file with validation and atomic write."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "PredictIQ-Dataset-Acquisition/2.0"})
    with tempfile.NamedTemporaryFile(dir=dest_path.parent, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        with urlopen(req, timeout=30) as resp:
            while chunk := resp.read(65536):
                tmp.write(chunk)
    actual_hash = compute_sha256(tmp_path)
    if actual_hash != expected_sha256:
        tmp_path.unlink(missing_ok=True)
        raise ValueError(f"Checksum mismatch for {dest_path.name}: expected {expected_sha256}, got {actual_hash}")
    tmp_path.replace(dest_path)


def read_arff_named(path: Path) -> pd.DataFrame:
    """Parse ARFF format using named attribute headers only."""
    attributes: list[str] = []
    data_lines: list[str] = []
    in_data = False
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("%"):
                continue
            if stripped.lower() == "@data":
                in_data = True
                continue
            if not in_data and stripped.lower().startswith("@attribute"):
                match = re.match(r"@attribute\s+(?:'([^']+)'|\"([^\"]+)\"|(\S+))\s+", stripped, re.IGNORECASE)
                if match:
                    name = next(g for g in match.groups() if g is not None)
                    attributes.append(name.strip())
            elif in_data:
                data_lines.append(stripped)
    data_io = io.StringIO("\n".join(data_lines))
    df = pd.read_csv(data_io, header=None, names=attributes, na_values=["?"])
    return df


def load_dataset(spec: SourceSpec, path: Path) -> pd.DataFrame:
    """Load and parse dataset using named columns."""
    if path.name == "aptness.dat.txt":
        # JSE Aptness fixed-width / whitespace table
        # Columns: id, size_fp, effort_hours, duration_months, os, dbms, language
        df = pd.read_csv(
            path,
            sep=r"\s+",
            header=None,
            names=["id", "size_fp", "effort_hours", "duration_months", "os", "dbms", "language"],
        )
        return df
    elif path.suffix == ".csv":
        return pd.read_csv(path, na_values=["?"])
    elif path.suffix == ".arff":
        return read_arff_named(path)
    raise ValueError(f"Unsupported format: {path.name}")


def verify_china_fix(china_path: Path) -> None:
    """Rigorously verify that China effort uses the Effort column, not Resource code."""
    df = read_arff_named(china_path)
    assert "Effort" in df.columns, "China dataset must have 'Effort' column"
    assert "Resource" in df.columns, "China dataset has 'Resource' code column"
    
    # Project 1: AFP=1587, Effort=7490, Resource=4
    p1 = df[df["ID"] == 1].iloc[0]
    effort_val = float(p1["Effort"])
    resource_val = float(p1["Resource"])
    assert effort_val == 7490.0, f"Expected China Project 1 effort 7490, got {effort_val}"
    assert resource_val == 4.0, f"Expected China Project 1 resource 4, got {resource_val}"
    assert effort_val != resource_val, "Effort must NOT match resource code!"
    
    # Check that effort distribution is realistic project hours (> 50 hours for 90%+ of projects)
    valid_efforts = pd.to_numeric(df["Effort"], errors="coerce").dropna()
    assert (valid_efforts > 50).mean() > 0.90, "Over 90% of China projects must have >50 person-hours"


def acquire_and_verify_all(data_dir: Path = ROOT_DATA_DIR) -> list[dict]:
    """Ensure all approved sources exist, match checksums, and parse correctly."""
    data_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    
    for spec in SOURCES:
        file_path = data_dir / spec.filename
        if not file_path.exists():
            print(f"Downloading {spec.name} from {spec.url}...")
            download_file(spec.url, file_path, spec.expected_sha256)
        
        # Verify hash
        actual_sha = compute_sha256(file_path)
        if actual_sha != spec.expected_sha256:
            raise ValueError(f"Checksum mismatch for {spec.name}: {actual_sha} != {spec.expected_sha256}")
        
        # Load and verify rows
        df = load_dataset(spec, file_path)
        assert spec.size_field in df.columns, f"Size field {spec.size_field} missing from {spec.name}"
        assert spec.effort_field in df.columns, f"Effort field {spec.effort_field} missing from {spec.name}"
        
        # Verify China fix specifically
        if spec.name == "China":
            verify_china_fix(file_path)
        
        summary.append({
            "Source": spec.name,
            "File": spec.filename,
            "Rows": len(df),
            "Size Field": spec.size_field,
            "Effort Field": spec.effort_field,
            "SHA-256 Checksum": actual_sha[:16] + "...",
            "Status": "VERIFIED",
        })
    
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Acquire and verify PredictIQ datasets")
    parser.add_argument("--dir", type=Path, default=ROOT_DATA_DIR, help="Target data directory")
    args = parser.parse_args()
    
    print("=" * 80)
    print("PredictIQ v2 — Dataset Acquisition & Verification Pipeline")
    print("=" * 80)
    
    summary = acquire_and_verify_all(args.dir)
    sum_df = pd.DataFrame(summary)
    print(sum_df.to_string(index=False))
    print("=" * 80)
    print(f"Total Approved Datasets Verified: {len(summary)}")
    total_rows = sum(s["Rows"] for s in summary)
    print(f"Total Combined Raw Records: {total_rows}")
    print("All SHA-256 digests and named-column mappings match contract.")


if __name__ == "__main__":
    main()
