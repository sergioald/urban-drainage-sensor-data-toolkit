import pandas as pd

from urban_drainage_sensor_toolkit.hydrology import (
    antecedent_dry_period_hours,
    calculate_time_to_peak,
    compute_flow_balance,
    summarise_sensor_response,
)


def test_calculate_time_to_peak_and_summary():
    response = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=4, freq="h"),
            "value": [1.0, 2.0, 5.0, 3.0],
        }
    )

    assert calculate_time_to_peak(response, event_start="2026-01-01 00:00") == 2.0
    summary = summarise_sensor_response(response, event_start="2026-01-01 00:00")
    assert summary["peak_value"] == 5.0
    assert summary["samples"] == 4


def test_compute_flow_balance():
    upstream = pd.DataFrame(
        {"timestamp": pd.date_range("2026-01-01", periods=3, freq="h"), "flow_lps": [10, 12, 14]}
    )
    downstream = pd.DataFrame(
        {"timestamp": pd.date_range("2026-01-01", periods=3, freq="h"), "flow_lps": [11, 13, 15]}
    )

    balance = compute_flow_balance(upstream, downstream)

    assert "flow_difference_lps" in balance.columns
    assert balance["flow_difference_lps"].tolist() == [1, 1, 1]


def test_antecedent_dry_period_hours():
    rainfall = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=6, freq="h"),
            "rainfall_mm": [0, 1, 0, 0, 2, 0],
        }
    )

    dry = antecedent_dry_period_hours(rainfall, event_start="2026-01-01 04:00")

    assert dry == 3.0
