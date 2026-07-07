"""Synthetic network demo report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from .events import detect_rainfall_events, join_sensor_response_to_events, summarise_events
from .maps import render_leaflet_map
from .status_rules import (
    classify_battery_voltage,
    classify_data_delay,
    classify_flatline,
    classify_flow_threshold,
    classify_level_threshold,
)
from .synthetic_network import create_synthetic_network_frames, write_synthetic_network


def run_synthetic_network_demo(
    output_folder: str | Path,
    *,
    periods: int = 336,
    freq: str = "30min",
) -> dict[str, Path]:
    """Run the synthetic urban drainage network demo."""

    output = Path(output_folder)
    data_dir = output / "data"
    output.mkdir(parents=True, exist_ok=True)

    paths = write_synthetic_network(data_dir, periods=periods, freq=freq)
    frames = create_synthetic_network_frames(periods=periods, freq=freq)

    rainfall = frames["rain_gauge_001"]
    level_1 = frames["level_sensor_001"]
    level_2 = frames["level_sensor_002"]
    flow = frames["flow_sensor_001"]
    points = frames["monitoring_points"]

    events = detect_rainfall_events(rainfall)
    events_csv = output / "event_summary.csv"
    events.to_csv(events_csv, index=False)

    level_response = pd.concat(
        [
            level_1.rename(columns={"level_m": "value"}),
            level_2.rename(columns={"level_m": "value"}),
        ],
        ignore_index=True,
    )
    flow_response = flow.rename(columns={"flow_lps": "value"})

    level_response_summary = join_sensor_response_to_events(
        level_response,
        events,
        value_col="value",
        response_window_hours=8,
    )
    flow_response_summary = join_sensor_response_to_events(
        flow_response,
        events,
        value_col="value",
        response_window_hours=8,
    )
    level_response_summary["response_type"] = "level_m"
    flow_response_summary["response_type"] = "flow_lps"
    response_summary = pd.concat([level_response_summary, flow_response_summary], ignore_index=True)
    response_csv = output / "sensor_response_summary.csv"
    response_summary.to_csv(response_csv, index=False)

    status_summary = _status_summary(
        rainfall=rainfall,
        level_1=level_1,
        level_2=level_2,
        flow=flow,
    )
    status_csv = output / "status_summary.csv"
    status_summary.to_csv(status_csv, index=False)

    network_summary = _network_summary(events, response_summary, status_summary)
    network_summary_csv = output / "network_summary.csv"
    network_summary.to_csv(network_summary_csv, index=False)

    plot_path = _write_network_plot(rainfall, level_1, level_2, flow, output / "rainfall_level_flow.png")
    map_path = render_leaflet_map(
        _points_for_map(points, status_summary),
        output / "synthetic_monitoring_points.html",
        title="Synthetic urban drainage network dashboard",
    )
    html_path = _write_network_report(
        output / "report.html",
        network_summary=network_summary,
        event_summary=events,
        response_summary=response_summary,
        status_summary=status_summary,
        plot_path=plot_path,
        map_path=map_path,
    )

    generated = {
        "report_html": html_path,
        "network_summary_csv": network_summary_csv,
        "event_summary_csv": events_csv,
        "sensor_response_summary_csv": response_csv,
        "status_summary_csv": status_csv,
        "rainfall_level_flow_plot": plot_path,
        "synthetic_map_html": map_path,
    }
    generated.update({f"data_{name}": path for name, path in paths.items()})
    return generated


def _status_summary(
    *,
    rainfall: pd.DataFrame,
    level_1: pd.DataFrame,
    level_2: pd.DataFrame,
    flow: pd.DataFrame,
) -> pd.DataFrame:
    all_timestamps = pd.concat(
        [
            rainfall["timestamp"],
            level_1["timestamp"],
            level_2["timestamp"],
            flow["timestamp"],
        ]
    )
    now = pd.to_datetime(all_timestamps).max() + pd.Timedelta(hours=1)

    rows = [
        _sensor_status_row(
            rainfall,
            point_id="RAIN_001",
            value_col="rainfall_mm",
            now=now,
            asset_type="rainfall",
        ),
        _sensor_status_row(
            level_1,
            point_id="LEVEL_001",
            value_col="level_m",
            now=now,
            asset_type="level",
            level_warning_high=0.65,
            level_critical_high=0.80,
        ),
        _sensor_status_row(
            level_2,
            point_id="LEVEL_002",
            value_col="level_m",
            now=now,
            asset_type="level",
            level_warning_high=0.58,
            level_critical_high=0.75,
        ),
        _sensor_status_row(
            flow,
            point_id="FLOW_001",
            value_col="flow_lps",
            now=now,
            asset_type="flow",
            flow_warning_high=28.0,
            flow_critical_high=34.0,
        ),
    ]
    return pd.DataFrame(rows)


def _sensor_status_row(
    df: pd.DataFrame,
    *,
    point_id: str,
    value_col: str,
    now: pd.Timestamp,
    asset_type: str,
    level_warning_high: float | None = None,
    level_critical_high: float | None = None,
    flow_warning_high: float | None = None,
    flow_critical_high: float | None = None,
) -> dict[str, object]:
    work = df.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
    work = work.dropna(subset=["timestamp"]).sort_values("timestamp")

    last_timestamp = work["timestamp"].max()
    latest_battery = work["battery_voltage"].dropna().iloc[-1] if "battery_voltage" in work else None
    recent_values = work[value_col].tail(8) if value_col in work else []

    if asset_type == "level":
        threshold_status = classify_level_threshold(
            work[value_col].max(),
            warning_high=level_warning_high,
            critical_high=level_critical_high,
        )
    elif asset_type == "flow":
        threshold_status = classify_flow_threshold(
            work[value_col].max(),
            warning_high=flow_warning_high,
            critical_high=flow_critical_high,
        )
    else:
        threshold_status = "not_applicable"

    return {
        "point_id": point_id,
        "asset_type": asset_type,
        "last_contact_status": classify_data_delay(last_timestamp, now=now),
        "battery_status": classify_battery_voltage(latest_battery),
        "flatline_status": classify_flatline(recent_values),
        "threshold_status": threshold_status,
        "latest_timestamp": last_timestamp.isoformat(),
    }


def _network_summary(
    events: pd.DataFrame,
    response_summary: pd.DataFrame,
    status_summary: pd.DataFrame,
) -> pd.DataFrame:
    event_metrics = summarise_events(events)
    status_counts = status_summary[["last_contact_status", "battery_status", "flatline_status", "threshold_status"]].apply(
        lambda col: int((col.astype(str) != "ok").sum())
    )

    rows = [
        {"metric": "rainfall_events", "value": event_metrics["event_count"]},
        {"metric": "total_rainfall_mm", "value": event_metrics["total_rainfall_mm"]},
        {"metric": "response_rows", "value": int(len(response_summary))},
        {"metric": "non_ok_status_flags", "value": int(status_counts.sum())},
    ]
    return pd.DataFrame(rows)


def _write_network_plot(
    rainfall: pd.DataFrame,
    level_1: pd.DataFrame,
    level_2: pd.DataFrame,
    flow: pd.DataFrame,
    output_png: Path,
) -> Path:
    fig = Figure(figsize=(10.5, 6.2))
    FigureCanvas(fig)
    ax1 = fig.subplots()
    ax2 = ax1.twinx()

    rain_ts = pd.to_datetime(rainfall["timestamp"])
    ax1.bar(rain_ts, rainfall["rainfall_mm"], width=0.018, alpha=0.45, label="Rainfall mm")
    ax1.set_ylabel("Rainfall depth per interval (mm)")
    ax1.invert_yaxis()

    ax2.plot(pd.to_datetime(level_1["timestamp"]), level_1["level_m"], linewidth=1.6, label="LEVEL_001 level")
    ax2.plot(pd.to_datetime(level_2["timestamp"]), level_2["level_m"], linewidth=1.6, label="LEVEL_002 level")
    ax2.plot(pd.to_datetime(flow["timestamp"]), flow["flow_lps"] / 50.0, linewidth=1.2, label="FLOW_001 flow / 50")
    ax2.set_ylabel("Level (m) and scaled flow")

    ax1.set_title("Synthetic rainfall, level and flow response")
    ax1.set_xlabel("Time")
    ax1.grid(alpha=0.25)

    handles_1, labels_1 = ax1.get_legend_handles_labels()
    handles_2, labels_2 = ax2.get_legend_handles_labels()
    ax2.legend(handles_1 + handles_2, labels_1 + labels_2, loc="upper right")

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_png, dpi=180, bbox_inches="tight")
    return output_png


def _points_for_map(points: pd.DataFrame, status_summary: pd.DataFrame) -> pd.DataFrame:
    status = status_summary.copy()
    status["status"] = status.apply(_dashboard_status, axis=1)

    merged = points.merge(
        status[["point_id", "status", "last_contact_status", "battery_status", "flatline_status", "threshold_status"]],
        on="point_id",
        how="left",
    )
    merged["last_contact_hours"] = 1.0
    merged["data_delayed"] = merged["last_contact_status"].astype(str).isin({"warning", "critical", "missing"})
    merged["battery_warning"] = merged["battery_status"].astype(str).isin({"warning", "critical", "missing"})
    merged["level_low"] = False
    merged["flow_high"] = merged["threshold_status"].astype(str).str.contains("high", na=False)
    merged["sensor_dirty"] = merged["flatline_status"].astype(str).eq("warning")
    merged["missing_data"] = merged["last_contact_status"].astype(str).eq("missing")
    return merged


def _dashboard_status(row: pd.Series) -> str:
    values = {
        str(row.get("last_contact_status", "")),
        str(row.get("battery_status", "")),
        str(row.get("flatline_status", "")),
        str(row.get("threshold_status", "")),
    }
    if "critical" in values or "critical_high" in values:
        return "offline"
    if "warning" in values or "warning_high" in values:
        return "warning"
    return "normal"


def _write_network_report(
    output_html: Path,
    *,
    network_summary: pd.DataFrame,
    event_summary: pd.DataFrame,
    response_summary: pd.DataFrame,
    status_summary: pd.DataFrame,
    plot_path: Path,
    map_path: Path,
) -> Path:
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Synthetic urban drainage network demo</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1120px; margin: 2rem auto; line-height: 1.45; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; margin-bottom: 2rem; }}
th, td {{ border: 1px solid #ddd; padding: 0.4rem; text-align: left; vertical-align: top; }}
th {{ background: #f3f3f3; }}
img {{ max-width: 100%; border: 1px solid #ddd; margin-bottom: 2rem; }}
.note {{ background: #eef7ff; border: 1px solid #b7d7f0; padding: 0.8rem; }}
</style>
</head>
<body>
<h1>Synthetic urban drainage network demo</h1>
<p class="note">Public-safe synthetic demonstration: rainfall-event detection, hydraulic response summaries, sensor status rules, dashboard-style map generation, and automated reporting.</p>

<h2>Rainfall, level and flow response</h2>
<img src="{plot_path.name}" alt="Synthetic rainfall, level and flow response plot">

<h2>Network summary</h2>
{network_summary.to_html(index=False, escape=True)}

<h2>Rainfall event summary</h2>
{event_summary.to_html(index=False, escape=True) if not event_summary.empty else "<p>No rainfall events detected.</p>"}

<h2>Sensor response summary</h2>
{response_summary.to_html(index=False, escape=True) if not response_summary.empty else "<p>No sensor responses summarised.</p>"}

<h2>Status summary</h2>
{status_summary.to_html(index=False, escape=True)}

<h2>Synthetic map</h2>
<p>Open <a href="{map_path.name}">{map_path.name}</a> locally to view the synthetic dashboard map.</p>
</body>
</html>
"""
    output_html.write_text(html, encoding="utf-8")
    return output_html
