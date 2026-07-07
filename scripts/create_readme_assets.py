"""Create public-safe README visual assets.

Run from the repository root:

    python scripts/create_readme_assets.py

Outputs:

    docs/assets/workflow_overview.png
    docs/assets/synthetic_anomaly_screening.png
    docs/assets/synthetic_map_preview.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = REPO_ROOT / "docs" / "assets"


def create_workflow_overview() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")

    steps = [
        ("Synthetic telemetry", "CSV files with flow, level,\nrainfall and device-status data"),
        ("QA/QC cleaning", "timestamps, duplicates,\nmissing records, daily summaries"),
        ("Public report", "HTML + CSV summaries\nfor software review"),
        ("Optional AI", "sensor-health features\nand robust anomaly scores"),
        ("Synthetic map", "fictional points and\npublic-safe coordinates"),
    ]

    x_positions = np.linspace(0.08, 0.92, len(steps))
    y = 0.55
    for i, (title, subtitle) in enumerate(steps):
        x = x_positions[i]
        box = plt.Rectangle(
            (x - 0.085, y - 0.12),
            0.17,
            0.24,
            fill=False,
            linewidth=1.8,
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x, y + 0.04, title, ha="center", va="center", fontsize=10, fontweight="bold", transform=ax.transAxes)
        ax.text(x, y - 0.045, subtitle, ha="center", va="center", fontsize=8.3, transform=ax.transAxes)
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(x_positions[i + 1] - 0.09, y),
                xytext=(x + 0.09, y),
                xycoords=ax.transAxes,
                arrowprops={"arrowstyle": "->", "linewidth": 1.5},
            )

    ax.text(
        0.5,
        0.9,
        "Urban drainage sensor-data QA/QC workflow",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.18,
        "Public-safe demonstration: synthetic data only, no real coordinates, no client identifiers, no credentials.",
        ha="center",
        va="center",
        fontsize=10,
        transform=ax.transAxes,
    )

    output = ASSET_DIR / "workflow_overview.png"
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output


def create_anomaly_plot() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(7)
    n = 240
    time = pd.date_range("2026-01-01", periods=n, freq="h")
    baseline = 1.2 + 0.15 * np.sin(np.linspace(0, 10 * np.pi, n))
    noise = rng.normal(0, 0.035, n)
    level = baseline + noise
    anomaly_idx = np.array([48, 96, 97, 160, 205])
    level[anomaly_idx] += np.array([0.35, -0.32, -0.28, 0.42, 0.30])

    median = np.median(level)
    mad = np.median(np.abs(level - median))
    score = np.abs(0.6745 * (level - median) / mad)
    is_anomaly = score > 4.0

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(time, level, linewidth=1.6, label="Synthetic level signal")
    ax.scatter(time[is_anomaly], level[is_anomaly], s=45, marker="x", label="Screened anomalies")
    ax.set_title("Synthetic anomaly-screening output")
    ax.set_xlabel("Time")
    ax.set_ylabel("Level")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    output = ASSET_DIR / "synthetic_anomaly_screening.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output


def create_map_preview() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    points = pd.DataFrame(
        [
            ("Point_001", "normal", 55.945, -3.205),
            ("Point_002", "warning", 55.952, -3.193),
            ("Point_003", "normal", 55.939, -3.184),
            ("Point_004", "offline", 55.934, -3.213),
            ("Point_005", "normal", 55.926, -3.198),
        ],
        columns=["point_id", "status", "latitude", "longitude"],
    )

    fig, ax = plt.subplots(figsize=(8, 5.2))
    markers = {"normal": "o", "warning": "^", "offline": "s"}
    for status, group in points.groupby("status"):
        ax.scatter(group["longitude"], group["latitude"], s=80, marker=markers.get(status, "o"), label=status)
        for _, row in group.iterrows():
            ax.annotate(
                row["point_id"],
                (row["longitude"], row["latitude"]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
            )

    ax.set_title("Synthetic monitoring-point map preview")
    ax.set_xlabel("Synthetic longitude")
    ax.set_ylabel("Synthetic latitude")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Status")
    fig.tight_layout()

    output = ASSET_DIR / "synthetic_map_preview.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output


def main() -> None:
    outputs = [
        create_workflow_overview(),
        create_anomaly_plot(),
        create_map_preview(),
    ]

    for output in outputs:
        print(f"Wrote {output.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
