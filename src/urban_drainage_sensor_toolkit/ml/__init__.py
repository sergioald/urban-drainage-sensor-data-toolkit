"""Optional applied-AI utilities for sensor-health screening.

These functions are intentionally lightweight and transparent. They are designed
for synthetic examples and local private-data exploration, not as a validated
production ML model.
"""

from .anomaly_baseline import robust_zscore, score_anomalies
from .features import build_sensor_health_features
from .sensor_health import summarise_sensor_health

__all__ = [
    "build_sensor_health_features",
    "robust_zscore",
    "score_anomalies",
    "summarise_sensor_health",
]
