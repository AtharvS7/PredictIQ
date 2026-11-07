import pandas as pd
from app.services import benchmark


def test_invalid_dataset_is_not_used_and_stale_cache_is_cleared(monkeypatch):
    monkeypatch.setattr(benchmark, "_benchmark_df", pd.DataFrame({"size_fp": [100], "effort_hours": [4]}))
    monkeypatch.setattr(benchmark, "require_unrevoked", lambda path, blocked: (_ for _ in ()).throw(ValueError("revoked")))
    benchmark.load_benchmark_data()
    assert benchmark._benchmark_df is None
    assert "unavailable" in benchmark.get_benchmark_comparison(100, 1000, 75000, 6).lower()


def test_valid_dataset_is_loaded():
    benchmark.load_benchmark_data()
    assert benchmark._benchmark_df is not None
    assert len(benchmark._benchmark_df) == 915
