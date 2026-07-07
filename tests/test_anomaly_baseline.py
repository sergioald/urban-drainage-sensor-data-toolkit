import pandas as pd

from urban_drainage_sensor_toolkit.ml import (
    build_sensor_health_features,
    score_anomalies,
    summarise_sensor_health,
)


def test_score_anomalies_flags_large_spike():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2020-01-01", periods=21, freq="h"),
            "level_m": [1.0] * 10 + [20.0] + [1.0] * 10,
        }
    )

    features = build_sensor_health_features(df, value_cols=["level_m"], rolling_window=3)
    scores = score_anomalies(features, threshold=3.0)

    assert "anomaly_score" in scores.columns
    assert scores["is_anomaly"].sum() >= 1

    summary = summarise_sensor_health(features, scores)
    assert int(summary.loc[0, "rows"]) == len(df)
