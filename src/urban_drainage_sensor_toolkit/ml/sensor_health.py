"""Sensor-health summaries from anomaly scores and features."""

from __future__ import annotations

import pandas as pd


def summarise_sensor_health(
    features: pd.DataFrame,
    scores: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    """Create a compact sensor-health summary table."""

    total_rows = len(features)
    if total_rows == 0:
        return pd.DataFrame(
            [
                {
                    "rows": 0,
                    "anomaly_rows": 0,
                    "anomaly_fraction": 0.0,
                    "missing_fraction": 0.0,
                    "flatline_fraction": 0.0,
                }
            ]
        )

    missing_cols = [col for col in features.columns if col.endswith("__missing")]
    flatline_cols = [col for col in features.columns if col.endswith("__flatline")]

    missing_fraction = features[missing_cols].mean(axis=1).mean() if missing_cols else 0.0
    flatline_fraction = features[flatline_cols].mean(axis=1).mean() if flatline_cols else 0.0
    anomaly_rows = int(scores["is_anomaly"].sum()) if "is_anomaly" in scores else 0

    summary = {
        "rows": total_rows,
        "anomaly_rows": anomaly_rows,
        "anomaly_fraction": round(anomaly_rows / total_rows, 4),
        "missing_fraction": round(float(missing_fraction), 4),
        "flatline_fraction": round(float(flatline_fraction), 4),
    }

    if timestamp_col in features.columns:
        summary["start"] = features[timestamp_col].min()
        summary["end"] = features[timestamp_col].max()

    return pd.DataFrame([summary])
