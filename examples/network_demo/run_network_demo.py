"""Run the synthetic urban drainage network demo.

Run from the repository root:

    python examples/network_demo/run_network_demo.py

or use the installed CLI:

    urban-drainage-qaqc network-demo
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from urban_drainage_sensor_toolkit.network_report import run_synthetic_network_demo  # noqa: E402


def main() -> None:
    output = REPO_ROOT / "examples" / "outputs" / "network_demo"
    generated = run_synthetic_network_demo(output)

    print(f"Network report written to: {generated['report_html']}")
    print(f"Event summary written to: {generated['event_summary_csv']}")
    print(f"Status summary written to: {generated['status_summary_csv']}")
    print(f"Synthetic dashboard map written to: {generated['synthetic_map_html']}")


if __name__ == "__main__":
    main()
