"""Evaluation protocol and cross-validation splitters for PredictIQ v2.

Implements:
- LeaveOneSourceOutSplitter: primary validation protocol (out-of-domain transferability)
- RepeatedGroupedKFoldSplitter: secondary validation protocol
- Dataset loading and integrity assertions
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence

import numpy as np
import pandas as pd

DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "projects_v2.csv"
)

EXPECTED_SOURCES = [
    "china",
    "kitchenham",
    "att_aptness",
    "desharnais",
    "maxwell",
    "albrecht",
]


@dataclass(frozen=True)
class FoldSplit:
    """Structured container for a single validation fold."""

    fold_name: str
    train_indices: np.ndarray
    test_indices: np.ndarray
    train_project_ids: list[str]
    test_project_ids: list[str]
    train_df: pd.DataFrame
    test_df: pd.DataFrame

    def verify_disjoint(self) -> None:
        """Verify train and test project IDs are strictly disjoint."""
        intersection = set(self.train_project_ids).intersection(set(self.test_project_ids))
        if intersection:
            raise ValueError(
                f"Data leakage detected in fold '{self.fold_name}': "
                f"{len(intersection)} project IDs overlap between train and test: {sorted(intersection)[:5]}"
            )


def load_dataset(path: Path | str | None = None) -> pd.DataFrame:
    """Load and validate the harmonized projects_v2.csv dataset.

    Parameters
    ----------
    path : Path | str | None
        Path to CSV file. Defaults to backend/ml/data/projects_v2.csv.

    Returns
    -------
    pd.DataFrame
        Loaded and verified DataFrame.
    """
    dataset_path = Path(path) if path is not None else DEFAULT_DATASET_PATH
    if not dataset_path.exists():
        raise FileNotFoundError(f"PredictIQ dataset not found at: {dataset_path}")

    df = pd.read_csv(dataset_path)

    required_columns = ["project_id", "source", "size_value", "effort_hours"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    if len(df) == 0:
        raise ValueError("Dataset is empty.")

    if not df["project_id"].is_unique:
        raise ValueError("Dataset contains non-unique project_id values.")

    if (df["size_value"] <= 0).any() or not np.isfinite(df["size_value"]).all():
        raise ValueError("Dataset contains non-positive or non-finite size_value entries.")

    if (df["effort_hours"] <= 0).any() or not np.isfinite(df["effort_hours"]).all():
        raise ValueError("Dataset contains non-positive or non-finite effort_hours entries.")

    return df


class LeaveOneSourceOutSplitter:
    """Leave-One-Source-Out (LOSO) Cross-Validation Splitter.

    In each fold, all projects from one historical data source are held out
    as the test set, while all remaining sources form the training set.
    Guarantees strict out-of-domain transferability testing without leakage.
    """

    def __init__(self, sources: Sequence[str] | None = None) -> None:
        """Initialize splitter.

        Parameters
        ----------
        sources : Sequence[str] | None
            Explicit sequence/order of source names to hold out. If None,
            detected dynamically preserving order of first appearance or EXPECTED_SOURCES.
        """
        self.sources = list(sources) if sources is not None else None

    def get_sources(self, groups: Sequence[str]) -> list[str]:
        """Return ordered list of unique sources."""
        if self.sources is not None:
            return self.sources

        unique_seen: list[str] = []
        for g in groups:
            if g not in unique_seen:
                unique_seen.append(g)

        # If detected sources match expected sources set, sort according to EXPECTED_SOURCES
        if set(unique_seen) == set(EXPECTED_SOURCES):
            return [s for s in EXPECTED_SOURCES if s in unique_seen]
        return unique_seen

    def get_n_splits(
        self,
        X: Any = None,
        y: Any = None,
        groups: Sequence[str] | None = None,
    ) -> int:
        """Return total number of folds (one per source)."""
        if groups is not None:
            return len(self.get_sources(groups))
        if hasattr(X, "columns") and "source" in getattr(X, "columns", []):
            return len(self.get_sources(X["source"].tolist()))
        if self.sources is not None:
            return len(self.sources)
        return len(EXPECTED_SOURCES)

    def split(
        self,
        X: Any,
        y: Any = None,
        groups: Sequence[str] | None = None,
    ) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        """Generate indices to split data into training and test sets.

        Parameters
        ----------
        X : array-like or pd.DataFrame
            Feature data. If groups is None and X is a DataFrame with 'source',
            'source' column will be used as groups.
        y : array-like, optional
            Target values.
        groups : Sequence[str], optional
            Source labels per sample.

        Yields
        ------
        train_idx : np.ndarray
        test_idx : np.ndarray
        """
        if groups is None:
            if hasattr(X, "columns") and "source" in getattr(X, "columns", []):
                source_series = np.asarray(X["source"])
            else:
                raise ValueError("Must provide 'groups' or an X DataFrame containing a 'source' column.")
        else:
            source_series = np.asarray(groups)

        n_samples = len(source_series)
        indices = np.arange(n_samples)
        unique_sources = self.get_sources(source_series)

        for holdout_source in unique_sources:
            test_mask = source_series == holdout_source
            train_mask = ~test_mask

            train_idx = indices[train_mask]
            test_idx = indices[test_mask]

            if len(test_idx) == 0:
                continue

            yield train_idx, test_idx

    def split_df(self, df: pd.DataFrame) -> Iterator[FoldSplit]:
        """Generate high-level FoldSplit objects from a pandas DataFrame.

        Verifies that train and test project IDs are strictly disjoint for each fold.
        """
        if "source" not in df.columns:
            raise ValueError("DataFrame must contain 'source' column.")
        if "project_id" not in df.columns:
            raise ValueError("DataFrame must contain 'project_id' column.")

        groups = df["source"].tolist()
        unique_sources = self.get_sources(groups)

        for holdout_source in unique_sources:
            train_mask = df["source"] != holdout_source
            test_mask = df["source"] == holdout_source

            train_df = df.loc[train_mask].copy()
            test_df = df.loc[test_mask].copy()

            train_indices = np.where(train_mask.to_numpy())[0]
            test_indices = np.where(test_mask.to_numpy())[0]

            split_obj = FoldSplit(
                fold_name=str(holdout_source),
                train_indices=train_indices,
                test_indices=test_indices,
                train_project_ids=train_df["project_id"].tolist(),
                test_project_ids=test_df["project_id"].tolist(),
                train_df=train_df,
                test_df=test_df,
            )
            # Strict leakage assertion
            split_obj.verify_disjoint()
            yield split_obj


class RepeatedGroupedKFoldSplitter:
    """Repeated K-Fold Cross-Validation splitter grouped by a cluster/source variable.

    Ensures that observations belonging to the same group/cluster never appear
    in both training and test partitions within the same repeat.
    """

    def __init__(
        self,
        n_splits: int = 5,
        n_repeats: int = 5,
        random_state: int = 42,
        shuffle: bool = True,
    ) -> None:
        if n_splits < 2:
            raise ValueError("n_splits must be at least 2.")
        if n_repeats < 1:
            raise ValueError("n_repeats must be at least 1.")

        self.n_splits = n_splits
        self.n_repeats = n_repeats
        self.random_state = random_state
        self.shuffle = shuffle

    def get_n_splits(
        self,
        X: Any = None,
        y: Any = None,
        groups: Sequence[Any] | None = None,
    ) -> int:
        """Return total number of splits across all repeats."""
        return self.n_splits * self.n_repeats

    def split(
        self,
        X: Any,
        y: Any = None,
        groups: Sequence[Any] | None = None,
    ) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        """Generate train/test indices for repeated grouped k-fold.

        Parameters
        ----------
        X : array-like or pd.DataFrame
        y : array-like, optional
        groups : Sequence[Any], optional
            Grouping / cluster variable. If None and X is DataFrame, checks 'source' or 'cluster'.
        """
        if groups is None:
            if hasattr(X, "columns"):
                if "cluster" in X.columns:
                    group_arr = np.asarray(X["cluster"])
                elif "source" in X.columns:
                    group_arr = np.asarray(X["source"])
                else:
                    raise ValueError("groups must be provided or exist as 'cluster' or 'source' in X.")
            else:
                raise ValueError("Must provide 'groups' for RepeatedGroupedKFoldSplitter.")
        else:
            group_arr = np.asarray(groups)

        n_samples = len(group_arr)
        indices = np.arange(n_samples)

        unique_groups = np.unique(group_arr)
        n_groups = len(unique_groups)

        if self.n_splits > n_groups:
            raise ValueError(
                f"Cannot have n_splits={self.n_splits} greater than the number of groups ({n_groups})."
            )

        for repeat_idx in range(self.n_repeats):
            rng = np.random.RandomState(self.random_state + repeat_idx if self.random_state is not None else None)
            shuffled_groups = unique_groups.copy()
            if self.shuffle:
                rng.shuffle(shuffled_groups)

            # Partition groups into n_splits folds
            group_folds: list[list[Any]] = [[] for _ in range(self.n_splits)]
            # Distribute groups round-robin or by count
            for i, group in enumerate(shuffled_groups):
                group_folds[i % self.n_splits].append(group)

            for fold_idx in range(self.n_splits):
                test_group_set = set(group_folds[fold_idx])
                test_mask = np.isin(group_arr, list(test_group_set))
                train_mask = ~test_mask

                train_idx = indices[train_mask]
                test_idx = indices[test_mask]

                # Assert strict group disjointness
                train_groups = set(group_arr[train_idx])
                test_groups = set(group_arr[test_idx])
                if not train_groups.isdisjoint(test_groups):
                    raise ValueError(
                        f"RepeatedGroupedKFold group leakage in repeat {repeat_idx}, fold {fold_idx}: "
                        f"{train_groups.intersection(test_groups)}"
                    )

                yield train_idx, test_idx
