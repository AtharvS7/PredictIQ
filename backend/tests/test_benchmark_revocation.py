import pandas as pd
from app.services import benchmark


def test_invalid_dataset_is_not_used_and_stale_cache_is_cleared(monkeypatch):
    monkeypatch.setattr(benchmark, "_benchmark_df", pd.DataFrame({"size_fp": [100], "effort_hours": [4]}))
    benchmark.load_benchmark_data()
    assert benchmark._benchmark_df is None
    assert "unavailable" in benchmark.get_benchmark_comparison(100, 1000, 75000, 6).lower()
