"""Synthetic multi-sensor urban drainage network generator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def create_synthetic_network_frames(
    *,
    start: str = "2026-01-01 00:00:00",
    periods: int = 336,
    freq: str = "30min",
    seed: int = 42,
) -> dict[str, pd.DataFrame]:
    """Create a synthetic rainfall, level, flow and battery monitoring network.

    The generator works for short test windows as well as the default two-week
    demo. Synthetic data-quality issues are inserted only where the requested
    number of records is long enough.
    """

    if periods < 1:
        raise ValueError("periods must be at least 1")

    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(start=start, periods=periods, freq=freq)

    rainfall = _rainfall_signal(periods)
    response = _exponential_response(rainfall, decay=0.90)

    rain_df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "point_id": "RAIN_001",
            "rainfall_mm": rainfall,
            "battery_voltage": 12.7 - np.linspace(0, 0.25, periods),
            "signal_quality": np.clip(98 - rainfall * 0.5 + rng.normal(0, 0.5, periods), 80, 100),
        }
    )

    level_1 = 0.42 + 0.025 * response + rng.normal(0, 0.006, periods)
    level_2 = 0.36 + 0.018 * np.roll(response, 2) + rng.normal(0, 0.006, periods)
    flow = 18 + 1.8 * np.roll(response, 1) + rng.normal(0, 0.4, periods)

    _insert_synthetic_quality_issues(level_1=level_1, level_2=level_2, flow=flow)

    level_1_df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "point_id": "LEVEL_001",
            "level_m": level_1,
            "battery_voltage": 12.5 - np.linspace(0, 0.35, periods),
        }
    )
    level_2_df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "point_id": "LEVEL_002",
            "level_m": level_2,
            "battery_voltage": 12.2 - np.linspace(0, 0.55, periods),
        }
    )
    flow_df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "point_id": "FLOW_001",
            "flow_lps": flow,
            "battery_voltage": 12.6 - np.linspace(0, 0.20, periods),
        }
    )

    battery_df = pd.concat(
        [
            rain_df[["timestamp", "point_id", "battery_voltage"]],
            level_1_df[["timestamp", "point_id", "battery_voltage"]],
            level_2_df[["timestamp", "point_id", "battery_voltage"]],
            flow_df[["timestamp", "point_id", "battery_voltage"]],
        ],
        ignore_index=True,
    )

    points_df = pd.DataFrame(
        {
            "point_id": ["RAIN_001", "LEVEL_001", "LEVEL_002", "FLOW_001"],
            "asset_type": ["rainfall", "level", "level", "flow"],
            "network": ["Synthetic_North", "Synthetic_Central", "Synthetic_South", "Synthetic_Central"],
            "latitude": [55.949, 55.944, 55.936, 55.941],
            "longitude": [-3.207, -3.198, -3.205, -3.191],
        }
    )

    return {
        "rain_gauge_001": rain_df,
        "level_sensor_001": level_1_df,
        "level_sensor_002": level_2_df,
        "flow_sensor_001": flow_df,
        "battery_status": battery_df,
        "monitoring_points": points_df,
    }


def write_synthetic_network(
    output_dir: str | Path,
    *,
    start: str = "2026-01-01 00:00:00",
    periods: int = 336,
    freq: str = "30min",
    seed: int = 42,
) -> dict[str, Path]:
    """Write synthetic network CSV files and return their paths."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    frames = create_synthetic_network_frames(start=start, periods=periods, freq=freq, seed=seed)
    paths = {}
    for name, frame in frames.items():
        path = output / f"{name}.csv"
        frame.to_csv(path, index=False)
        paths[name] = path
    return paths


def _insert_synthetic_quality_issues(
    *,
    level_1: np.ndarray,
    level_2: np.ndarray,
    flow: np.ndarray,
) -> None:
    """Insert synthetic quality issues without assuming a fixed array length."""

    periods = len(level_1)
    if periods == 0:
        return

    # Flatline window. Use a proportional index so short test windows still work.
    if periods >= 12:
        flat_start = min(max(4, periods // 2), periods - 2)
        flat_end = min(flat_start + min(8, max(2, periods // 12)), periods)
        reference_idx = max(flat_start - 1, 0)
        level_1[flat_start:flat_end] = level_1[reference_idx]

    # Missing-data window.
    if periods >= 16:
        missing_start = min(max(8, int(periods * 0.65)), periods - 1)
        missing_end = min(missing_start + min(5, max(1, periods // 20)), periods)
        level_2[missing_start:missing_end] = np.nan

    # Flow spike.
    if periods >= 8:
        spike_idx = min(max(4, int(periods * 0.78)), periods - 1)
        flow[spike_idx] += 12


def _rainfall_signal(periods: int) -> np.ndarray:
    rainfall = np.zeros(periods)
    event_slices = [
        (24, [0.3, 0.8, 1.5, 2.2, 1.1, 0.4]),
        (96, [0.4, 1.2, 3.0, 4.0, 2.5, 1.0, 0.2]),
        (210, [0.5, 0.9, 1.6, 1.8, 0.9]),
    ]

    for start, values in event_slices:
        end = min(start + len(values), periods)
        if start < periods:
            rainfall[start:end] = values[: end - start]
    return rainfall


def _exponential_response(rainfall: np.ndarray, *, decay: float) -> np.ndarray:
    response = np.zeros_like(rainfall, dtype=float)
    for i, value in enumerate(rainfall):
        previous = response[i - 1] if i else 0.0
        response[i] = previous * decay + value
    return response
