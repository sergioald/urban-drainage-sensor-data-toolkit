# Optional applied-AI extension

The repository includes a small optional applied-AI example for sensor-health
screening.

The example converts synthetic telemetry into features for missing values,
rolling mean and standard deviation, rate of change, spikes, flat-line behaviour,
and basic row-level anomaly scores.

The default detector uses robust z-scores based on the median absolute deviation.
This makes the result explainable and suitable as a baseline.

This is not a validated production ML model. It does not use private operational
data, and it does not claim predictive performance on real drainage networks.

Run the demo:

```bash
python examples/ml/run_anomaly_demo.py
```
