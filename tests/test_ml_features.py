import pandas as pd

from urban_drainage_sensor_toolkit.ml import build_sensor_health_features


def test_build_sensor_health_features_basic():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2020-01-01", periods=6, freq="h"),
            "level_m": [1.0, 1.1, 1.2, 1.2, 5.0, 1.3],
            "flow_l_s": [10, 11, 12, 12, 80, 13],
        }
    )

    features = build_sensor_health_features(
        df,
        value_cols=["level_m", "flow_l_s"],
        rolling_window=3,
    )

    assert "level_m__rolling_mean" in features.columns
    assert "flow_l_s__abs_diff" in features.columns
    assert "level_m__missing" in features.columns
    assert len(features) == len(df)
