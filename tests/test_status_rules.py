import pandas as pd

from urban_drainage_sensor_toolkit.status_rules import (
    classify_battery_voltage,
    classify_data_delay,
    classify_flatline,
    classify_flow_threshold,
    classify_level_threshold,
    summarise_status_flags,
)


def test_classify_data_delay():
    now = pd.Timestamp("2026-01-04 00:00:00")

    assert classify_data_delay("2026-01-03 12:00:00", now=now) == "ok"
    assert classify_data_delay("2026-01-02 12:00:00", now=now) == "warning"
    assert classify_data_delay("2026-01-01 00:00:00", now=now) == "critical"
    assert classify_data_delay(None, now=now) == "missing"


def test_battery_and_flatline_rules():
    assert classify_battery_voltage(12.5) == "ok"
    assert classify_battery_voltage("11,7") == "warning"
    assert classify_battery_voltage(11.0) == "critical"
    assert classify_flatline([1, 1, 1, 1, 1, 1]) == "warning"
    assert classify_flatline([1, 1.1, 1, 1.2, 1, 1.3]) == "ok"


def test_threshold_rules():
    assert classify_level_threshold(0.2, warning_low=0.3, critical_low=0.1) == "warning_low"
    assert classify_level_threshold(0.05, warning_low=0.3, critical_low=0.1) == "critical_low"
    assert classify_flow_threshold(10.5, warning_high=8.0, critical_high=10.0) == "critical_high"


def test_summarise_status_flags():
    flags = summarise_status_flags(
        last_timestamp="2026-01-02",
        now="2026-01-04",
        battery_voltage=11.7,
        recent_values=[1, 1, 1, 1, 1, 1],
        flow=12,
        flow_warning_high=8,
        flow_critical_high=10,
    )

    assert flags["data_delay"] == "warning"
    assert flags["battery"] == "warning"
    assert flags["flatline"] == "warning"
    assert flags["flow"] == "critical_high"
