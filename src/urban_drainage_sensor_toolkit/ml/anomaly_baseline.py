"""Transparent baseline anomaly scoring.

The robust z-score/MAD approach is suitable for a public synthetic demo and for
private exploratory screening when labels are unavailable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def robust_zscore(series: pd.Series) -> pd.Series:
    """Return a robust z-score using the median absolute deviation."""

    values = pd.to_numeric(series, errors="coerce")
    median = values.median(skipna=True)
    mad = (values - median).abs().median(skipna=True)

    if pd.isna(mad) or mad == 0:
        std = values.std(skipna=True)
        if pd.isna(std) or std == 0:
            non_missing = values.notna().astype(float)
            return pd.Series(np.zeros(len(values)), index=series.index, dtype=float) * non_missing
        return (values - median) / std

    return 0.6745 * (values - median) / mad


def score_anomalies(
    features: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    threshold: float = 4.0,
) -> pd.DataFrame:
    """Score rows using the maximum robust z-score across numeric features."""

    if features.empty:
        return pd.DataFrame(columns=[timestamp_col, "anomaly_score", "is_anomaly"])

    numeric_cols = [
        col
        for col in features.select_dtypes(include=[np.number]).columns
        if not col.endswith("__missing")
    ]

    result = pd.DataFrame(index=features.index)

    if timestamp_col in features.columns:
        result[timestamp_col] = features[timestamp_col]

    if not numeric_cols:
        result["anomaly_score"] = 0.0
        result["dominant_feature"] = ""
        result["is_anomaly"] = False
        return result

    zscores = pd.DataFrame(
        {col: robust_zscore(features[col]).abs() for col in numeric_cols},
        index=features.index,
    )

    result["anomaly_score"] = zscores.max(axis=1).fillna(0.0)
    result["dominant_feature"] = zscores.idxmax(axis=1)
    result["is_anomaly"] = result["anomaly_score"] >= threshold
    return result
