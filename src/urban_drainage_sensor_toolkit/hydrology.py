"""Simple hydraulic-response metrics for public-safe demonstrations."""

from __future__ import annotations

import pandas as pd


def calculate_time_to_peak(
    response: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    value_col: str = "value",
    event_start: pd.Timestamp | str,
) -> float | None:
    """Return time to peak in hours from an event start."""

    if response.empty:
        return None

    work = response[[timestamp_col, value_col]].copy()
    work[timestamp_col] = pd.to_datetime(work[timestamp_col], errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[timestamp_col, value_col])
    if work.empty:
        return None

    peak_idx = work[value_col].idxmax()
    peak_ts = pd.to_datetime(work.loc[peak_idx, timestamp_col])
    start = pd.to_datetime(event_start)
    return float((peak_ts - start).total_seconds() / 3600.0)


def summarise_sensor_response(
    response: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    value_col: str = "value",
    event_start: pd.Timestamp | str | None = None,
) -> dict[str, float | int | None]:
    """Return transparent response metrics for one sensor window."""

    if response.empty:
        return {
            "samples": 0,
            "start_value": None,
            "mean_value": None,
            "peak_value": None,
            "min_value": None,
            "time_to_peak_hours": None,
        }

    values = pd.to_numeric(response[value_col], errors="coerce").dropna()
    if values.empty:
        return {
            "samples": 0,
            "start_value": None,
            "mean_value": None,
            "peak_value": None,
            "min_value": None,
            "time_to_peak_hours": None,
        }

    return {
        "samples": int(len(values)),
        "start_value": float(values.iloc[0]),
        "mean_value": float(values.mean()),
        "peak_value": float(values.max()),
        "min_value": float(values.min()),
        "time_to_peak_hours": (
            calculate_time_to_peak(
                response,
                timestamp_col=timestamp_col,
                value_col=value_col,
                event_start=event_start,
            )
            if event_start is not None
            else None
        ),
    }


def compute_flow_balance(
    upstream: pd.DataFrame,
    downstream: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    flow_col: str = "flow_lps",
    tolerance: str = "30min",
) -> pd.DataFrame:
    """Compare upstream and downstream flow series using nearest timestamps."""

    left = upstream[[timestamp_col, flow_col]].copy()
    right = downstream[[timestamp_col, flow_col]].copy()

    left[timestamp_col] = pd.to_datetime(left[timestamp_col], errors="coerce")
    right[timestamp_col] = pd.to_datetime(right[timestamp_col], errors="coerce")
    left[flow_col] = pd.to_numeric(left[flow_col], errors="coerce")
    right[flow_col] = pd.to_numeric(right[flow_col], errors="coerce")

    left = left.dropna().sort_values(timestamp_col).rename(columns={flow_col: "upstream_flow_lps"})
    right = right.dropna().sort_values(timestamp_col).rename(columns={flow_col: "downstream_flow_lps"})

    merged = pd.merge_asof(
        left,
        right,
        on=timestamp_col,
        tolerance=pd.Timedelta(tolerance),
        direction="nearest",
    )
    merged["flow_difference_lps"] = merged["downstream_flow_lps"] - merged["upstream_flow_lps"]
    merged["flow_ratio"] = merged["downstream_flow_lps"] / merged["upstream_flow_lps"].replace(0, pd.NA)
    return merged


def antecedent_dry_period_hours(
    rainfall: pd.DataFrame,
    *,
    event_start: pd.Timestamp | str,
    timestamp_col: str = "timestamp",
    rainfall_col: str = "rainfall_mm",
) -> float | None:
    """Return hours since the previous wet rainfall record before an event."""

    work = rainfall[[timestamp_col, rainfall_col]].copy()
    work[timestamp_col] = pd.to_datetime(work[timestamp_col], errors="coerce")
    work[rainfall_col] = pd.to_numeric(work[rainfall_col], errors="coerce").fillna(0)
    work = work.dropna(subset=[timestamp_col]).sort_values(timestamp_col)

    start = pd.to_datetime(event_start)
    previous_wet = work[(work[timestamp_col] < start) & (work[rainfall_col] > 0)]
    if previous_wet.empty:
        return None

    last_wet = previous_wet[timestamp_col].max()
    return float((start - last_wet).total_seconds() / 3600.0)
