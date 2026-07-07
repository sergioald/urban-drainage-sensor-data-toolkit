"""Create public-safe README visual assets.

Run from the repository root:

    python scripts/create_readme_assets.py

Outputs:

    docs/assets/workflow_overview.png
    docs/assets/synthetic_anomaly_screening.png
    docs/assets/synthetic_monitoring_dashboard_preview.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

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
        ("Synthetic map", "dashboard-style map\nwith fictional points"),
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


def _load_font(size: int) -> ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_panel(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(xy, radius=8, fill=fill, outline=(185, 185, 185, 220), width=1)


def create_dashboard_map_preview() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    width, height = 1600, 900
    image = Image.new("RGB", (width, height), (15, 17, 20))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_panel = _load_font(18)
    font_small = _load_font(14)
    font_tiny = _load_font(12)

    rng = np.random.default_rng(12)

    # Synthetic dark basemap texture.
    for _ in range(130):
        x0 = int(rng.integers(0, width))
        y0 = int(rng.integers(0, height))
        length = int(rng.integers(90, 280))
        angle = float(rng.uniform(0, 2 * np.pi))
        points = []
        for step in range(5):
            x = x0 + int(np.cos(angle + 0.22 * step) * length * step / 5)
            y = y0 + int(np.sin(angle + 0.18 * step) * length * step / 5)
            points.append((x, y))
        draw.line(points, fill=(68, 72, 78, 90), width=int(rng.integers(1, 3)))

    # Fictional green boundaries, inspired by operational overlays but synthetic.
    boundary_sets = [
        [(455, 90), (640, 105), (720, 210), (690, 340), (545, 385), (410, 300), (455, 90)],
        [(700, 375), (900, 320), (1060, 430), (1020, 610), (815, 645), (655, 535), (700, 375)],
        [(215, 430), (385, 370), (540, 470), (510, 675), (320, 720), (185, 595), (215, 430)],
        [(1080, 170), (1320, 145), (1445, 310), (1370, 505), (1150, 500), (1035, 335), (1080, 170)],
    ]
    for pts in boundary_sets:
        jittered = []
        for x, y in pts:
            jittered.append((x + int(rng.integers(-18, 18)), y + int(rng.integers(-18, 18))))
        draw.line(jittered, fill=(16, 170, 38, 235), width=5)

    # Synthetic markers and clusters.
    marker_data = [
        (600, 290, "warning", "▲", "8"),
        (665, 310, "normal", "●", "17"),
        (710, 325, "offline", "■", "29"),
        (760, 365, "warning", "▲", "5"),
        (835, 395, "offline", "■", "12"),
        (920, 465, "normal", "●", "21"),
        (1045, 495, "warning", "▲", "6"),
        (470, 510, "offline", "■", "3"),
        (370, 580, "normal", "●", "2"),
        (1220, 360, "warning", "▲", "4"),
        (1285, 610, "offline", "■", "1"),
        (760, 575, "normal", "●", "10"),
        (905, 250, "normal", "●", "15"),
        (555, 420, "offline", "■", "7"),
    ]
    colours = {
        "normal": (44, 162, 95, 255),
        "warning": (254, 178, 76, 255),
        "offline": (222, 45, 38, 255),
    }
    for x, y, status, symbol, label in marker_data:
        fill = colours[status]
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=fill, outline=(255, 255, 255, 230), width=2)
        draw.text((x - 6, y - 10), symbol, fill=(255, 255, 255, 255), font=font_tiny)
        draw.text((x + 13, y + 9), label, fill=(235, 210, 190, 230), font=font_tiny)

    # Left zoom buttons and search.
    _draw_panel(draw, (12, 54, 44, 124), (255, 255, 255, 238))
    draw.text((23, 59), "+", fill=(20, 20, 20, 255), font=font_panel)
    draw.line((17, 89, 39, 89), fill=(150, 150, 150, 255), width=1)
    draw.text((25, 91), "–", fill=(20, 20, 20, 255), font=font_panel)

    _draw_panel(draw, (14, 140, 150, 178), (255, 255, 255, 238))
    draw.text((24, 149), "ID PDM", fill=(70, 70, 70, 255), font=font_small)
    draw.text((116, 147), "⌕", fill=(20, 20, 20, 255), font=font_panel)

    # Header.
    _draw_panel(draw, (55, 18, 560, 88), (18, 18, 18, 225))
    draw.text((75, 28), "Synthetic urban drainage monitoring dashboard", fill=(250, 250, 250, 255), font=font_panel)
    draw.text((75, 58), "Public-safe mock-up: fictional IDs, synthetic coordinates and QA/QC flags.", fill=(210, 210, 210, 255), font=font_small)

    # Right control panel.
    _draw_panel(draw, (1340, 56, 1580, 845), (255, 255, 255, 238))
    draw.text((1360, 76), "Layers and QA/QC filters", fill=(25, 25, 25, 255), font=font_panel)

    y = 120
    sections = [
        ("Base map", ["● cartodb dark matter", "○ openstreetmap"]),
        ("Overlay", ["☑ Synthetic regions", "☑ Cluster points"]),
        ("Status", ["☑ Normal", "☑ Warning", "☑ Offline", "☑ Maintenance"]),
        ("QA/QC flags", ["☑ Data delayed", "☑ Battery warning", "☑ Low level", "☑ High flow", "☑ Dirty sensor", "☑ Missing data"]),
    ]
    for title, items in sections:
        draw.text((1360, y), title, fill=(25, 25, 25, 255), font=font_small)
        y += 25
        for item in items:
            draw.text((1370, y), item, fill=(45, 45, 45, 255), font=font_tiny)
            y += 24
        y += 10

    # Attribution-like footer.
    draw.rectangle((1120, 868, 1585, 895), fill=(250, 250, 250, 220))
    draw.text((1132, 873), "Synthetic preview | Inspired by Leaflet dashboards | No real operational data", fill=(20, 80, 120, 255), font=font_tiny)

    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    output = ASSET_DIR / "synthetic_monitoring_dashboard_preview.png"
    image.save(output)
    return output


def main() -> None:
    outputs = [
        create_workflow_overview(),
        create_anomaly_plot(),
        create_dashboard_map_preview(),
    ]

    for output in outputs:
        print(f"Wrote {output.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
