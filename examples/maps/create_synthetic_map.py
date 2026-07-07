"""Create a public-safe synthetic monitoring dashboard map.

Run from the repository root:

    python examples/maps/create_synthetic_map.py

The output is written to:

    examples/outputs/synthetic_map/synthetic_monitoring_points.html
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from urban_drainage_sensor_toolkit.cli import _run_map_demo  # noqa: E402


def main() -> None:
    generated = _run_map_demo(REPO_ROOT / "examples" / "outputs" / "synthetic_map")
    print(f"Synthetic point table written to: {generated['csv']}")
    print(f"Synthetic dashboard map written to: {generated['html']}")


if __name__ == "__main__":
    main()
