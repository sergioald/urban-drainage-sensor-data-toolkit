# Synthetic dashboard-style map example

The original private workflow produced interactive map-style outputs for
monitoring points. Those maps should not be published because they can expose
real coordinates, client names, project identifiers, operational asset IDs, and
network status.

This public example keeps the same *software idea* but replaces all sensitive
content with a synthetic dashboard mock-up.

## What the public example reflects

The map demonstrates:

- a dark Leaflet-style monitoring interface
- synthetic monitoring-point markers
- fictional basin/region boundaries
- point clustering
- a search box for fictional point IDs
- layer controls
- QA/QC filters for delayed data, battery status, low level, high flow, dirty
  sensors, and missing data
- popups with synthetic point metadata

## Run

```bash
python examples/maps/create_synthetic_map.py
```

## Outputs

```text
examples/outputs/synthetic_map/
├── synthetic_monitoring_points.csv
└── synthetic_monitoring_points.html
```

## Public-safety rule

Only synthetic or anonymised points should be used in public examples. Do not
commit real coordinates, real client names, real project names, or operational
asset identifiers.
