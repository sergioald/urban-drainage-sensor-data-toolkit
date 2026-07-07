"""Add the synthetic network demo section to README.md.

Run from the repository root:

    python scripts/update_readme_network_demo.py
"""

from pathlib import Path

README = Path("README.md")

NETWORK_SECTION = """### 4. Synthetic multi-sensor network demo

Run:

```bash
urban-drainage-qaqc network-demo
```

Expected output:

```text
examples/outputs/network_demo/
├── report.html
├── network_summary.csv
├── event_summary.csv
├── sensor_response_summary.csv
├── status_summary.csv
├── rainfall_level_flow.png
├── synthetic_monitoring_points.html
└── data/
    ├── rain_gauge_001.csv
    ├── level_sensor_001.csv
    ├── level_sensor_002.csv
    ├── flow_sensor_001.csv
    ├── battery_status.csv
    └── monitoring_points.csv
```

The network demo shows the end-to-end public workflow: synthetic rainfall and sensor telemetry, event detection, hydraulic response summaries, status-rule checks, report generation, and a dashboard-style map.
"""


def main() -> None:
    text = README.read_text(encoding="utf-8")

    text = text.replace(
        "| Automated reporting | Static HTML, CSV summaries, and report-summary plots from synthetic telemetry |",
        "| Automated reporting | Static HTML, CSV summaries, report-summary plots, and synthetic network reports |",
    )
    text = text.replace(
        "| Urban hydrology monitoring | Flow, level, velocity, rainfall, battery, and last-contact style telemetry checks |",
        "| Urban hydrology monitoring | Flow, level, velocity, rainfall, battery, last-contact checks, event detection, and response summaries |",
    )
    text = text.replace(
        "synthetic monitoring-point map",
        "synthetic monitoring-point map / synthetic network demo",
    )

    marker = "---\n\n## Quick start with Anaconda"
    if "### 4. Synthetic multi-sensor network demo" not in text and marker in text:
        text = text.replace(marker, NETWORK_SECTION + "\n---\n\n## Quick start with Anaconda")

    map_quickstart = """Run the synthetic map demo:

```powershell
urban-drainage-qaqc map-demo
```"""
    network_quickstart = """Run the synthetic map demo:

```powershell
urban-drainage-qaqc map-demo
```

Run the synthetic network demo:

```powershell
urban-drainage-qaqc network-demo
```"""
    if "Run the synthetic network demo:" not in text:
        text = text.replace(map_quickstart, network_quickstart)

    command_usage_marker = """Keep private audit outputs outside Git or in ignored folders."""
    command_usage_insert = """Keep private audit outputs outside Git or in ignored folders.

Run the synthetic network demo:

```bash
urban-drainage-qaqc network-demo
```"""
    if command_usage_marker in text and "Run the synthetic network demo:\n\n```bash\nurban-drainage-qaqc network-demo" not in text:
        text = text.replace(command_usage_marker, command_usage_insert)

    text = _update_source_tree(text)

    README.write_text(text, encoding="utf-8")
    print("Updated README with synthetic network demo.")


def _update_source_tree(text: str) -> str:
    replacements = [
        (
            "├── reporting.py      # HTML/CSV report and plot generation\n├── status_rules.py",
            "├── network_report.py # synthetic network report generation\n├── reporting.py      # HTML/CSV report and plot generation\n├── status_rules.py",
        ),
        (
            "├── maps.py           # public-safe synthetic map generation\n├── network_report.py",
            "├── events.py         # rainfall-event detection and response joins\n├── hydrology.py      # simple hydraulic-response metrics\n├── maps.py           # public-safe synthetic map generation\n├── network_report.py",
        ),
        (
            "├── status_rules.py   # stale-data, battery, flatline, level and flow checks\n├── synthetic.py",
            "├── status_rules.py   # stale-data, battery, flatline, level and flow checks\n├── synthetic.py      # synthetic telemetry generation\n├── synthetic_network.py # synthetic multi-sensor network generation",
        ),
    ]

    for old, new in replacements:
        if old in text and new not in text:
            text = text.replace(old, new)

    return text


if __name__ == "__main__":
    main()
