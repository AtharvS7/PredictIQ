"""Regression coverage for source labels and leakage boundaries."""
import numpy as np
import pandas as pd
import pytest
from ml.rebuild_dataset import SOURCES, audit_legacy, read_source, reconstruct
from ml.train_research import candidates, conformal_radius, metrics, split_projects


def test_arff_maps_named_effort_not_resource(tmp_path):
    path = tmp_path / "china.arff"
    path.write_text("@relation china\n@attribute Resource numeric\n@attribute Effort numeric\n"
                    "@attribute ID numeric\n@attribute AFP numeric\n@attribute Input numeric\n"
                    "@attribute Output numeric\n@attribute Enquiry numeric\n"
                    "@attribute File numeric\n@attribute Interface numeric\n"
                    "@data\n4,7490,1,1587,774,260,340,128,0\n")
    source = read_source(path)
    legacy = pd.DataFrame([{"size_fp": 1587, "Transactions": 1374, "Entities": 128, "effort_hours": 4}])
    audit = audit_legacy(legacy, source)
    assert audit["resource_codes_used_as_hours"] == 1
    assert audit["examples"][0]["source_hours"] == 7490
    legacy.loc[0, "effort_hours"] = 7490
    assert audit_legacy(legacy, source)["resource_codes_used_as_hours"] == 0


def test_reconstruct_preserves_large_labels_and_excludes_missing_size(tmp_path):
    for name, identifier, size, effort in SOURCES.values():
        columns = ([identifier] if identifier else []) + [size, effort]
        rows = (["1,20,50000", "2,?,100"] if identifier else ["20,50000", "?,100"])
        if name.endswith("csv"):
            (tmp_path / name).write_text(",".join(columns) + "\n" + "\n".join(rows).replace("?", ""))
        else:
            header = "@relation test\n" + "".join(f"@attribute {c} numeric\n" for c in columns)
            (tmp_path / name).write_text(header + "@data\n" + "\n".join(rows))
    data, report = reconstruct(tmp_path)
    assert len(data) == 4
    assert set(data.effort_hours) == {50000}
    assert data.duplicate_group.nunique() == 1
    assert all(source["excluded_missing_or_nonpositive"] == 1 for source in report.values())


def test_duplicate_projects_never_cross_split_boundaries():
    data = pd.DataFrame({"duplicate_group": np.repeat(np.arange(50), 2)})
    partitions = split_projects(data)
    groups = [set(data.iloc[index].duplicate_group) for index in partitions]
    assert not groups[0] & groups[1]
    assert not groups[0] & groups[2]
    assert not groups[1] & groups[2]
    assert sum(map(len, partitions)) == len(data)


def test_metrics_use_actual_hours_and_finite_sample_calibration():
    result = metrics([100, 200], [100, 100])
    assert result["mae_hours"] == 50
    assert result["pred25_percent"] == 50
    assert result["median_absolute_percentage_error"] == 25
    with pytest.raises(ValueError):
        metrics([100], [np.nan])
    with pytest.raises(ValueError, match="Insufficient"):
        conformal_radius(np.ones(2), np.ones(2))


def test_model_bundle_round_trip_includes_preprocessing(tmp_path):
    import pickle

    x = pd.DataFrame({"size_fp": np.arange(1, 101)})
    model = candidates()["power_law_ridge"].fit(x, x.size_fp * 20)
    path = tmp_path / "candidate.pkl"
    path.write_bytes(pickle.dumps(model))
    loaded = pickle.loads(path.read_bytes())
    np.testing.assert_allclose(loaded.predict(x), model.predict(x))
