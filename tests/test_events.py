import pandas as pd

from urban_drainage_sensor_toolkit.events import (
    detect_rainfall_events,
    join_sensor_response_to_events,
    summarise_events,
)


def test_detect_rainfall_events_groups_wet_periods():
    rainfall = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=12, freq="h"),
            "rainfall_mm": [0, 0.5, 1.0, 0, 0, 0, 2.0, 1.0, 0, 0, 0, 0],
        }
    )

    events = detect_rainfall_events(rainfall, event_gap_hours=2, min_total_rainfall_mm=1)

    assert len(events) == 2
    assert events["total_rainfall_mm"].tolist() == [1.5, 3.0]


def test_summarise_events_empty_and_non_empty():
    empty = detect_rainfall_events(
        pd.DataFrame(
            {
                "timestamp": pd.date_range("2026-01-01", periods=3, freq="h"),
                "rainfall_mm": [0, 0, 0],
            }
        )
    )
    assert summarise_events(empty)["event_count"] == 0

    events = pd.DataFrame({"total_rainfall_mm": [1.0, 2.0], "duration_hours": [1.0, 3.0]})
    assert summarise_events(events)["total_rainfall_mm"] == 3.0


def test_join_sensor_response_to_events():
    events = pd.DataFrame(
        {
            "event_id": [1],
            "start": [pd.Timestamp("2026-01-01 00:00")],
            "end": [pd.Timestamp("2026-01-01 02:00")],
        }
    )
    sensor = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=6, freq="h"),
            "point_id": ["LEVEL_001"] * 6,
            "value": [0.1, 0.2, 0.5, 0.4, 0.3, 0.2],
        }
    )

    response = join_sensor_response_to_events(sensor, events, response_window_hours=3)

    assert len(response) == 1
    assert response.loc[0, "peak_value"] == 0.5
    assert response.loc[0, "time_to_peak_hours"] == 2.0
