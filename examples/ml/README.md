# Optional applied-AI anomaly-screening demo

This example shows how cleaned telemetry can be converted into transparent
sensor-health features and screened for anomalous behaviour.

It uses **synthetic data only**. It is not a trained production model and it is
not validated on private operational data.

Run from the repository root:

```bash
python examples/ml/run_anomaly_demo.py
```

Expected outputs:

```text
examples/outputs/ml_anomaly_demo/
├── anomaly_plot.png
├── anomaly_scores.csv
├── anomaly_summary.csv
└── sensor_health_features.csv
```
