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

from urban_drainage_sensor_toolkit.maps import (  # noqa: E402
    create_synthetic_monitoring_points,
    render_leaflet_map,
)


def main() -> None:
    output_dir = REPO_ROOT / "examples" / "outputs" / "synthetic_map"
    output_dir.mkdir(parents=True, exist_ok=True)

    points = create_synthetic_monitoring_points()
    points.to_csv(output_dir / "synthetic_monitoring_points.csv", index=False)

    output_html = render_leaflet_map(
        points,
        output_dir / "synthetic_monitoring_points.html",
        title="Synthetic urban drainage monitoring dashboard",
    )

    print(f"Synthetic point table written to: {output_dir / 'synthetic_monitoring_points.csv'}")
    print(f"Synthetic dashboard map written to: {output_html}")


if __name__ == "__main__":
    main()
