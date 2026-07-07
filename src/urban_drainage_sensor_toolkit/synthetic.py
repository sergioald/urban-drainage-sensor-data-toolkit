from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def create_synthetic_monitoring_csv(
    output_path: str | Path,
    *,
    point_name: str = "PDM_SYNTHETIC_001",
    start: str = "2026-01-01 00:00:00",
    periods: int = 192,
    frequency: str = "15min",
    seed: int = 42,
) -> Path:
    """Create a small public-safe CSV resembling a drainage telemetry export."""

    rng = np.random.default_rng(seed)
    ts = pd.date_range(start=start, periods=periods, freq=frequency)
    hour = ts.hour.to_numpy() + ts.minute.to_numpy() / 60.0

    water_level = 0.55 + 0.08 * np.sin(2 * np.pi * hour / 24) + rng.normal(0, 0.015, periods)
    velocity = 0.35 + 0.05 * np.cos(2 * np.pi * hour / 24) + rng.normal(0, 0.012, periods)
    flow = water_level * velocity * 950.0
    rainfall = rng.gamma(0.35, 1.8, periods)
    rainfall[rng.random(periods) < 0.82] = 0.0
    battery = 12.4 - np.linspace(0, 0.12, periods) + rng.normal(0, 0.02, periods)
    digital_event = np.where(water_level > np.quantile(water_level, 0.90), "HIGH_LEVEL", "NORMAL")

    df = pd.DataFrame(
        {
            "PDM": point_name,
            "DATA": ts.strftime("%d/%m/%Y"),
            "ORA": ts.strftime("%H:%M:%S"),
            "level_m": water_level.round(3),
            "velocity_m_s": velocity.round(3),
            "flow_l_s": flow.round(2),
            "rainfall_mm": rainfall.round(2),
            "battery_v": battery.round(2),
            "DIGITAL EVENT": digital_event,
        }
    )

    # Add one duplicate and one blank timestamp row to exercise cleaning behaviour.
    if periods > 10:
        df = pd.concat([df, df.iloc[[8]].assign(flow_l_s=df.iloc[8]["flow_l_s"] + 5.0)], ignore_index=True)
        df.loc[len(df)] = [point_name, "", "", np.nan, np.nan, np.nan, np.nan, np.nan, "NORMAL"]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep=";", index=False)
    return output_path
