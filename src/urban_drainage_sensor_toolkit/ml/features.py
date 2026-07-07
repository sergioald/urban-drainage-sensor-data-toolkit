"""Feature extraction for sensor-health and anomaly screening."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


def _available_columns(df: pd.DataFrame, requested: Iterable[str]) -> list[str]:
    return [col for col in requested if col in df.columns]


def build_sensor_health_features(
    df: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    value_cols: Iterable[str] | None = None,
    rolling_window: int = 12,
) -> pd.DataFrame:
    """Build transparent sensor-health features from a telemetry table.

    The output includes rolling means, rolling standard deviations, first
    differences, missing-value flags and flat-line flags.
    """

    if df.empty:
        return pd.DataFrame()

    work = df.copy()

    if timestamp_col in work.columns:
        work[timestamp_col] = pd.to_datetime(work[timestamp_col], errors="coerce")
        work = work.sort_values(timestamp_col).reset_index(drop=True)

    if value_cols is None:
        value_columns = [
            col
            for col in work.select_dtypes(include=[np.number]).columns
            if col != timestamp_col
        ]
    else:
        value_columns = _available_columns(work, value_cols)

    features = pd.DataFrame(index=work.index)

    if timestamp_col in work.columns:
        features[timestamp_col] = work[timestamp_col]

    for col in value_columns:
        series = pd.to_numeric(work[col], errors="coerce")
        diff = series.diff()
        features[col] = series
        features[f"{col}__missing"] = series.isna().astype(int)
        features[f"{col}__rolling_mean"] = series.rolling(rolling_window, min_periods=3).mean()
        features[f"{col}__rolling_std"] = series.rolling(rolling_window, min_periods=3).std()
        features[f"{col}__diff"] = diff
        features[f"{col}__abs_diff"] = diff.abs()
        features[f"{col}__flatline"] = (
            series.diff().abs().rolling(rolling_window, min_periods=3).sum().fillna(1) == 0
        ).astype(int)

    return features
