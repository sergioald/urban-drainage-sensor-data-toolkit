# Synthetic map example

The original private workflow produced map-style outputs for monitoring points.
The public repository should not include real point maps because they can expose
coordinates, client names, project identifiers, and asset IDs.

This synthetic example demonstrates the same kind of output safely.

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
