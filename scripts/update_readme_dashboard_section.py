"""Update README map references for the dashboard-style preview.

Run from the repository root:

    python scripts/update_readme_dashboard_section.py
"""

from pathlib import Path

README = Path("README.md")

OLD = """### Synthetic monitoring-point map

![Synthetic monitoring-point map preview](docs/assets/synthetic_map_preview.png)

The map example uses fictional point IDs and synthetic coordinates only. Do not commit real coordinates, client names, project names, or operational asset IDs.
"""

NEW = """### Synthetic monitoring dashboard map

![Synthetic monitoring dashboard map preview](docs/assets/synthetic_monitoring_dashboard_preview.png)

The dashboard-style map preview reflects the original private monitoring workflow more closely while remaining public-safe. It includes a dark map-style background, synthetic clustered points, fictional region boundaries, a search box, layer controls, and QA/QC filters. All points, coordinates, IDs, filters, and labels are synthetic.
"""


def main() -> None:
    text = README.read_text(encoding="utf-8")
    if OLD in text:
        text = text.replace(OLD, NEW)
    else:
        text = text.replace(
            "### Synthetic monitoring-point map",
            "### Synthetic monitoring dashboard map",
        )
        text = text.replace(
            "![Synthetic monitoring-point map preview](docs/assets/synthetic_map_preview.png)",
            "![Synthetic monitoring dashboard map preview](docs/assets/synthetic_monitoring_dashboard_preview.png)",
        )
        text = text.replace(
            "The map example uses fictional point IDs and synthetic coordinates only. Do not commit real coordinates, client names, project names, or operational asset IDs.",
            "The dashboard-style map preview reflects the original private monitoring workflow more closely while remaining public-safe. It includes a dark map-style background, synthetic clustered points, fictional region boundaries, a search box, layer controls, and QA/QC filters. All points, coordinates, IDs, filters, and labels are synthetic.",
        )

    text = text.replace(
        "python examples\\maps\\create_synthetic_map.py",
        "urban-drainage-qaqc map-demo",
    )
    text = text.replace(
        "python examples/maps/create_synthetic_map.py",
        "urban-drainage-qaqc map-demo",
    )

    README.write_text(text, encoding="utf-8")
    print("Updated README dashboard map references.")


if __name__ == "__main__":
    main()
