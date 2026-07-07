import warnings

import pandas as pd

from urban_drainage_sensor_toolkit.core import (
    build_timestamp,
    classify_contact,
    clean_timeseries,
    daily_aggregate,
    summarize_measurement_point,
)


def test_clean_timeseries_combines_data_ora_and_deduplicates():
    df = pd.DataFrame(
        {
            "DATA": ["01/01/2026", "01/01/2026", "01/01/2026", ""],
            "ORA": ["00:15:00", "00:00:00", "00:15:00", ""],
            "level_m": ["1,2", "1.0", "1.3", "bad"],
            "DIGITAL EVENT": [None, "NORMAL", None, "NORMAL"],
        }
    )
    cleaned = clean_timeseries(df)
    assert len(cleaned) == 2
    assert cleaned["timestamp"].is_monotonic_increasing
    assert cleaned.loc[1, "level_m"] == 1.3
    assert cleaned.loc[1, "DIGITAL EVENT"] == "NORMAL"


def test_build_timestamp_handles_iso_dataora_without_warning():
    df = pd.DataFrame({"DATAORA": ["2020-09-14 07:54:00", "", "not a date"]})
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        parsed = build_timestamp(df)
    assert not record
    assert parsed.notna().sum() == 1
    assert parsed.iloc[0] == pd.Timestamp("2020-09-14 07:54:00")


def test_summarize_measurement_point_estimates_missing_rows():
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2026-01-01 00:00", "2026-01-01 00:30"])})
    summary = summarize_measurement_point(df, expected_interval_seconds=900)
    assert summary.rows == 2
    assert summary.missing_rows_estimate == 1
    assert summary.median_step_seconds == 1800.0


def test_classify_contact_thresholds():
    now = pd.Timestamp("2026-01-04 00:00")
    assert classify_contact("2026-01-03 12:00", now=now) == "ok"
    assert classify_contact("2026-01-02 12:00", now=now) == "warning"
    assert classify_contact("2026-01-01 00:00", now=now) == "critical"
    assert classify_contact(None, now=now) == "missing"


def test_daily_aggregate_sums_rainfall_and_averages_level():
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-01-01 00:00", "2026-01-01 01:00"]),
            "rainfall_mm": [1.0, 2.5],
            "level_m": [0.4, 0.6],
        }
    )
    out = daily_aggregate(df)
    assert out.loc[0, "rainfall_mm"] == 3.5
    assert out.loc[0, "level_m"] == 0.5
