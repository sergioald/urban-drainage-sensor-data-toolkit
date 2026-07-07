# Synthetic map example

This example creates a public-safe synthetic Leaflet monitoring dashboard using
fictional points, synthetic coordinates, mock status flags, and dashboard-style
filters.

Run from the repository root:

```bash
python examples/maps/create_synthetic_map.py
```

Outputs:

```text
examples/outputs/synthetic_map/
├── synthetic_monitoring_points.csv
└── synthetic_monitoring_points.html
```

The generated HTML includes:

- a dark basemap
- synthetic point clusters
- fictional region boundaries
- search by synthetic point ID
- status filters
- QA/QC flag filters

Do not replace these synthetic points with real private coordinates, client
names, project names, or operational identifiers in a public repository.
