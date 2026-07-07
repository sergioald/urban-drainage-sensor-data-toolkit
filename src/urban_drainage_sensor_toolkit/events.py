"""Rainfall-event detection and sensor-response helpers.

The functions in this module are intentionally transparent and public-safe. They
operate on synthetic or anonymised telemetry tables and provide simple event
analytics that are useful for urban drainage monitoring demos.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def detect_rainfall_events(
    rainfall: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    rainfall_col: str = "rainfall_mm",
    event_gap_hours: float = 2.0,
    min_total_rainfall_mm: float = 1.0,
) -> pd.DataFrame:
    """Detect rainfall events from a rainfall time series.

    Wet records are rows where ``rainfall_col`` is greater than zero. Wet records
    separated by more than ``event_gap_hours`` start a new event. Events with
    total depth below ``min_total_rainfall_mm`` are discarded.
    """

    required = {timestamp_col, rainfall_col}
    missing = sorted(required.difference(rainfall.columns))
    if missing:
        raise ValueError(f"Missing required rainfall columns: {missing}")

    work = rainfall[[timestamp_col, rainfall_col]].copy()
    work[timestamp_col] = pd.to_datetime(work[timestamp_col], errors="coerce")
    work[rainfall_col] = pd.to_numeric(work[rainfall_col], errors="coerce").fillna(0.0)
    work = work.dropna(subset=[timestamp_col]).sort_values(timestamp_col)

    wet = work[work[rainfall_col] > 0].reset_index(drop=True)
    if wet.empty:
        return _empty_events()

    gap = pd.Timedelta(hours=event_gap_hours)
    event_ids = []
    current_event = 1
    previous_ts = wet.loc[0, timestamp_col]
    for _, row in wet.iterrows():
        ts = row[timestamp_col]
        if ts - previous_ts > gap:
            current_event += 1
        event_ids.append(current_event)
        previous_ts = ts

    wet["event_id"] = event_ids

    rows = []
    inferred_step = _infer_step(work[timestamp_col])
    for event_id, group in wet.groupby("event_id", sort=True):
        start = group[timestamp_col].min()
        last_wet = group[timestamp_col].max()
        end = last_wet + inferred_step
        total = float(group[rainfall_col].sum())
        if total < min_total_rainfall_mm:
            continue
        rows.append(
            {
                "event_id": int(event_id),
                "start": start,
                "end": end,
                "duration_hours": float((end - start).total_seconds() / 3600.0),
                "total_rainfall_mm": total,
                "peak_intensity_mm": float(group[rainfall_col].max()),
                "wet_records": int(len(group)),
            }
        )

    if not rows:
        return _empty_events()
    return pd.DataFrame(rows)


def summarise_events(events: pd.DataFrame) -> dict[str, float | int | None]:
    """Return compact rainfall-event summary metrics."""

    if events.empty:
        return {
            "event_count": 0,
            "total_rainfall_mm": 0.0,
            "max_event_depth_mm": None,
            "max_event_duration_hours": None,
        }

    return {
        "event_count": int(len(events)),
        "total_rainfall_mm": float(events["total_rainfall_mm"].sum()),
        "max_event_depth_mm": float(events["total_rainfall_mm"].max()),
        "max_event_duration_hours": float(events["duration_hours"].max()),
    }


def join_sensor_response_to_events(
    sensor: pd.DataFrame,
    events: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    value_col: str = "value",
    sensor_id_col: str | None = "point_id",
    response_window_hours: float = 6.0,
) -> pd.DataFrame:
    """Summarise sensor response during and after each rainfall event.

    The response window runs from event start to event end plus
    ``response_window_hours``. If ``sensor_id_col`` is present, one row is
    returned per sensor per event.
    """

    if events.empty:
        return _empty_response(sensor_id_col=sensor_id_col)

    required = {timestamp_col, value_col}
    missing = sorted(required.difference(sensor.columns))
    if missing:
        raise ValueError(f"Missing required sensor columns: {missing}")

    work = sensor.copy()
    work[timestamp_col] = pd.to_datetime(work[timestamp_col], errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[timestamp_col, value_col]).sort_values(timestamp_col)

    group_cols = [sensor_id_col] if sensor_id_col and sensor_id_col in work.columns else [None]
    rows = []

    for _, event in events.iterrows():
        start = pd.to_datetime(event["start"])
        end = pd.to_datetime(event["end"])
        window_end = end + pd.Timedelta(hours=response_window_hours)

        for group_value, group in _iter_groups(work, group_cols[0]):
            window = group[(group[timestamp_col] >= start) & (group[timestamp_col] <= window_end)]
            if window.empty:
                rows.append(
                    _empty_response_row(
                        event_id=int(event["event_id"]),
                        sensor_id=group_value,
                        sensor_id_col=group_cols[0],
                    )
                )
                continue

            peak_idx = window[value_col].idxmax()
            peak_ts = pd.to_datetime(window.loc[peak_idx, timestamp_col])
            rows.append(
                {
                    "event_id": int(event["event_id"]),
                    **({str(group_cols[0]): group_value} if group_cols[0] else {}),
                    "samples": int(len(window)),
                    "start_value": float(window[value_col].iloc[0]),
                    "mean_value": float(window[value_col].mean()),
                    "peak_value": float(window[value_col].max()),
                    "min_value": float(window[value_col].min()),
                    "time_to_peak_hours": float((peak_ts - start).total_seconds() / 3600.0),
                }
            )

    return pd.DataFrame(rows)


def write_events_csv(events: pd.DataFrame, output_csv: str | Path) -> Path:
    """Write an event table to CSV and return the path."""

    path = Path(output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(path, index=False)
    return path


def _infer_step(timestamps: pd.Series) -> pd.Timedelta:
    diffs = timestamps.sort_values().drop_duplicates().diff().dropna()
    if diffs.empty:
        return pd.Timedelta(0)
    return diffs.median()


def _iter_groups(df: pd.DataFrame, group_col: str | None):
    if group_col is None:
        yield None, df
    else:
        yield from df.groupby(group_col, sort=True)


def _empty_events() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "event_id",
            "start",
            "end",
            "duration_hours",
            "total_rainfall_mm",
            "peak_intensity_mm",
            "wet_records",
        ]
    )


def _empty_response(sensor_id_col: str | None) -> pd.DataFrame:
    columns = ["event_id"]
    if sensor_id_col:
        columns.append(sensor_id_col)
    columns += [
        "samples",
        "start_value",
        "mean_value",
        "peak_value",
        "min_value",
        "time_to_peak_hours",
    ]
    return pd.DataFrame(columns=columns)


def _empty_response_row(
    *,
    event_id: int,
    sensor_id: object,
    sensor_id_col: str | None,
) -> dict[str, object]:
    row: dict[str, object] = {
        "event_id": event_id,
        "samples": 0,
        "start_value": None,
        "mean_value": None,
        "peak_value": None,
        "min_value": None,
        "time_to_peak_hours": None,
    }
    if sensor_id_col:
        row[sensor_id_col] = sensor_id
    return row
