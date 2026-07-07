from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from .audit import audit_csv_file, find_csv_files
from .core import clean_timeseries, daily_aggregate, dataframe_profile, summarize_measurement_point
from .io_utils import read_monitoring_csv


def run_folder_report(
    input_folder: str | Path,
    output_folder: str | Path,
    *,
    recursive: bool = True,
    write_cleaned: bool = True,
) -> dict[str, Path]:
    """Run a public-safe QA/QC report over CSV files.

    The workflow is intentionally tolerant of mixed private-data folders. Files
    without standard timestamp columns are listed in the inventory and skipped
    from time-series cleaning instead of causing the report to fail.
    """

    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    summaries = []
    inventory_rows = []
    generated: dict[str, Path] = {}

    for csv_file in find_csv_files(input_folder, recursive=recursive):
        profile = audit_csv_file(csv_file, root=input_folder)
        inventory_rows.append(profile.as_dict())
        safe_stem = _safe_output_stem(csv_file.relative_to(input_folder))

        if profile.status in {"no_timestamp_columns", "no_valid_timestamps", "read_error"}:
            row = {
                "file": profile.relative_path,
                "dataset_kind": profile.dataset_kind,
                "status": f"skipped: {profile.status}",
                "rows": profile.rows,
                "valid_timestamps": profile.valid_timestamps,
                "start": profile.start,
                "end": profile.end,
                "duration_hours": None,
                "median_step_seconds": profile.median_step_seconds,
                "duplicate_timestamps": profile.duplicate_timestamps,
                "missing_rows_estimate": None,
                "digital_columns": profile.digital_columns,
            }
            summaries.append(row)
            continue

        try:
            raw = read_monitoring_csv(csv_file)
            cleaned = clean_timeseries(raw)
            summary = summarize_measurement_point(cleaned).as_dict()
            summary["file"] = profile.relative_path
            summary["dataset_kind"] = profile.dataset_kind
            summary["status"] = "processed"
            summaries.append(summary)

            if write_cleaned:
                clean_path = output_folder / f"{safe_stem}_cleaned.csv"
                cleaned.to_csv(clean_path, index=False)
                generated[f"cleaned_{safe_stem}"] = clean_path

            daily_path = output_folder / f"{safe_stem}_daily.csv"
            profile_path = output_folder / f"{safe_stem}_profile.csv"
            daily_aggregate(cleaned).to_csv(daily_path, index=False)
            dataframe_profile(cleaned).to_csv(profile_path, index=False)
            generated[f"daily_{safe_stem}"] = daily_path
            generated[f"profile_{safe_stem}"] = profile_path
        except Exception as exc:  # pragma: no cover - defensive for messy private folders
            summaries.append(
                {
                    "file": profile.relative_path,
                    "dataset_kind": profile.dataset_kind,
                    "status": f"failed: {type(exc).__name__}: {exc}",
                    "rows": profile.rows,
                    "valid_timestamps": profile.valid_timestamps,
                    "start": profile.start,
                    "end": profile.end,
                    "duration_hours": None,
                    "median_step_seconds": profile.median_step_seconds,
                    "duplicate_timestamps": profile.duplicate_timestamps,
                    "missing_rows_estimate": None,
                    "digital_columns": profile.digital_columns,
                }
            )

    inventory_df = pd.DataFrame(inventory_rows)
    inventory_csv = output_folder / "file_inventory.csv"
    inventory_df.to_csv(inventory_csv, index=False)
    generated["file_inventory_csv"] = inventory_csv

    summary_df = pd.DataFrame(summaries)
    summary_csv = output_folder / "summary.csv"
    summary_df.to_csv(summary_csv, index=False)
    generated["summary_csv"] = summary_csv

    report_summary_plot = _write_report_summary_plot(summary_df, output_folder)
    generated["report_summary_plot"] = report_summary_plot

    html_path = output_folder / "report.html"
    html = _build_html_report(summary_df, inventory_df, report_summary_plot=report_summary_plot.name)
    html_path.write_text(html, encoding="utf-8")
    generated["html_report"] = html_path
    return generated


def _safe_output_stem(relative_path: Path) -> str:
    stem = str(relative_path.with_suffix(""))
    for token in ("/", "\\", " ", ":"):
        stem = stem.replace(token, "__")
    return stem


def _status_bucket(status: object) -> str:
    text = str(status).lower()
    if text.startswith("processed"):
        return "processed"
    if text.startswith("skipped"):
        return "skipped"
    if text.startswith("failed"):
        return "failed"
    return "other"


def _numeric_column(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce").fillna(0)


def _write_report_summary_plot(summary_df: pd.DataFrame, output_folder: Path) -> Path:
    """Write one public-safe PNG plot summarising the QA/QC report.

    This uses Matplotlib's Agg canvas directly, so it does not require Tk or any
    desktop GUI backend in conda or CI environments.
    """

    output_path = output_folder / "report_summary.png"

    if summary_df.empty:
        metrics = pd.Series({"processed files": 0, "skipped files": 0, "failed files": 0})
    else:
        status_bucket = (
            summary_df["status"].map(_status_bucket)
            if "status" in summary_df
            else pd.Series(dtype=str)
        )
        metrics = pd.Series(
            {
                "processed files": int((status_bucket == "processed").sum()),
                "skipped files": int((status_bucket == "skipped").sum()),
                "failed files": int((status_bucket == "failed").sum()),
                "duplicate timestamps": int(_numeric_column(summary_df, "duplicate_timestamps").sum()),
                "missing rows estimate": int(_numeric_column(summary_df, "missing_rows_estimate").sum()),
            }
        )

    fig = Figure(figsize=(8.5, 4.8))
    FigureCanvas(fig)
    ax = fig.subplots()

    ordered = metrics.sort_values()
    positions = range(len(ordered))
    ax.barh(list(positions), ordered.to_numpy())
    ax.set_yticks(list(positions), labels=list(ordered.index))
    ax.set_title("Synthetic QA/QC report summary")
    ax.set_xlabel("Count")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.3)

    max_value = max(float(ordered.max()), 1.0)
    for i, value in enumerate(ordered.to_numpy()):
        ax.text(float(value) + max_value * 0.02, i, f"{int(value)}", va="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    return output_path


def _build_html_report(
    summary_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    *,
    report_summary_plot: str | None = None,
) -> str:
    summary_table = (
        summary_df.to_html(index=False, escape=True) if not summary_df.empty else "<p>No CSV files found.</p>"
    )
    inventory_table = (
        inventory_df[["relative_path", "dataset_kind", "timestamp_layout", "status", "rows", "columns"]]
        .to_html(index=False, escape=True)
        if not inventory_df.empty
        else "<p>No CSV files found.</p>"
    )
    plot_html = (
        f'<h2>Report summary plot</h2><img src="{report_summary_plot}" alt="QA/QC report summary plot">'
        if report_summary_plot
        else ""
    )
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<title>Urban drainage telemetry QA/QC report</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 2rem auto; line-height: 1.45; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; margin-bottom: 2rem; }}
th, td {{ border: 1px solid #ddd; padding: 0.4rem; text-align: left; vertical-align: top; }}
th {{ background: #f3f3f3; }}
img {{ max-width: 100%; border: 1px solid #ddd; margin-bottom: 2rem; }}
.note {{ background: #fff8dc; border: 1px solid #eedc82; padding: 0.8rem; }}
</style>
</head>
<body>
<h1>Urban drainage telemetry QA/QC report</h1>
<p class=\"note\">Public-safe demonstration report. It checks CSV structure, timestamps, duplicate records, digital-event columns, and simple daily aggregates. It does not replace engineering review. Original operational files should stay private.</p>
{plot_html}
<h2>Time-series summary</h2>
{summary_table}
<h2>File inventory</h2>
{inventory_table}
</body>
</html>
"""
