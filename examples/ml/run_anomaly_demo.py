"""Run a lightweight applied-AI anomaly-screening demo on synthetic data."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from urban_drainage_sensor_toolkit.ml import (  # noqa: E402
    build_sensor_health_features,
    score_anomalies,
    summarise_sensor_health,
)


def find_input_file() -> Path:
    candidates = [
        REPO_ROOT / "examples" / "data" / "synthetic_monitoring_point.csv",
        REPO_ROOT / "examples" / "outputs" / "synthetic_report" / "synthetic_monitoring_point_cleaned.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No synthetic input file found.")


def main() -> None:
    input_file = find_input_file()
    output_dir = REPO_ROOT / "examples" / "outputs" / "ml_anomaly_demo"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic/private-like exports may be comma- or semicolon-delimited.
    df = pd.read_csv(input_file, sep=None, engine="python")
    timestamp_candidates = ["timestamp", "DATAORA", "date_time", "datetime", "date", "DATA"]
    timestamp_col = next((col for col in timestamp_candidates if col in df.columns), df.columns[0])

    features = build_sensor_health_features(df, timestamp_col=timestamp_col)
    scores = score_anomalies(features, timestamp_col=timestamp_col)
    summary = summarise_sensor_health(features, scores, timestamp_col=timestamp_col)

    features.to_csv(output_dir / "sensor_health_features.csv", index=False)
    scores.to_csv(output_dir / "anomaly_scores.csv", index=False)
    summary.to_csv(output_dir / "anomaly_summary.csv", index=False)

    if timestamp_col in features.columns and len(features) > 0:
        first_numeric = [
            col for col in features.select_dtypes(include="number").columns if "__" not in col
        ]
        if first_numeric:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(features[timestamp_col], features[first_numeric[0]], linewidth=1)
            anomaly_mask = scores["is_anomaly"].to_numpy()
            ax.scatter(
                features.loc[anomaly_mask, timestamp_col],
                features.loc[anomaly_mask, first_numeric[0]],
                s=20,
                label="flagged anomaly",
            )
            ax.set_title("Synthetic sensor-health anomaly screening")
            ax.set_xlabel("time")
            ax.set_ylabel(first_numeric[0])
            ax.legend()
            fig.autofmt_xdate()
            fig.tight_layout()
            fig.savefig(output_dir / "anomaly_plot.png", dpi=150)
            plt.close(fig)

    print(f"Input: {input_file}")
    print(f"Outputs written to: {output_dir}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
