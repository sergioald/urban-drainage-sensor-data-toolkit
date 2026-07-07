"""Public-safe sensor status and QA/QC rule helpers.

The rules in this module are intentionally simple and transparent. They are
designed for public examples and software tests, not as a substitute for
site-specific engineering thresholds.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def classify_data_delay(
    last_timestamp: pd.Timestamp | str | None,
    *,
    now: pd.Timestamp | str | None = None,
    warning_after_hours: float = 24.0,
    critical_after_hours: float = 72.0,
) -> str:
    """Classify whether a monitoring point has stale data."""

    if last_timestamp is None or pd.isna(last_timestamp):
        return "missing"

    last = pd.to_datetime(last_timestamp, errors="coerce")
    if pd.isna(last):
        return "missing"

    current = pd.Timestamp.now() if now is None else pd.to_datetime(now)
    age_hours = (current - last).total_seconds() / 3600.0

    if age_hours < 0:
        return "future_timestamp"
    if age_hours >= critical_after_hours:
        return "critical"
    if age_hours >= warning_after_hours:
        return "warning"
    return "ok"


def classify_battery_voltage(
    voltage: float | int | str | None,
    *,
    warning_below: float = 11.8,
    critical_below: float = 11.2,
) -> str:
    """Classify a battery voltage using simple public-safe thresholds."""

    value = _to_float(voltage)
    if value is None:
        return "missing"
    if value <= critical_below:
        return "critical"
    if value <= warning_below:
        return "warning"
    return "ok"


def detect_flatline(
    values: Sequence[object] | pd.Series,
    *,
    min_points: int = 6,
    tolerance: float = 1e-9,
) -> bool:
    """Return True when recent numeric values are effectively constant."""

    series = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
    if len(series) < min_points:
        return False

    recent = series.tail(min_points)
    return bool((recent.max() - recent.min()) <= tolerance)


def classify_flatline(
    values: Sequence[object] | pd.Series,
    *,
    min_points: int = 6,
    tolerance: float = 1e-9,
) -> str:
    """Classify flat-line behaviour in a recent sensor window."""

    return "warning" if detect_flatline(values, min_points=min_points, tolerance=tolerance) else "ok"


def classify_threshold(
    value: float | int | str | None,
    *,
    warning_low: float | None = None,
    critical_low: float | None = None,
    warning_high: float | None = None,
    critical_high: float | None = None,
) -> str:
    """Classify one numeric value against low/high warning and critical thresholds."""

    numeric = _to_float(value)
    if numeric is None:
        return "missing"

    if critical_low is not None and numeric <= critical_low:
        return "critical_low"
    if critical_high is not None and numeric >= critical_high:
        return "critical_high"
    if warning_low is not None and numeric <= warning_low:
        return "warning_low"
    if warning_high is not None and numeric >= warning_high:
        return "warning_high"
    return "ok"


def classify_level_threshold(
    level: float | int | str | None,
    *,
    warning_low: float | None = None,
    critical_low: float | None = None,
    warning_high: float | None = None,
    critical_high: float | None = None,
) -> str:
    """Classify a level measurement using transparent threshold rules."""

    return classify_threshold(
        level,
        warning_low=warning_low,
        critical_low=critical_low,
        warning_high=warning_high,
        critical_high=critical_high,
    )


def classify_flow_threshold(
    flow: float | int | str | None,
    *,
    warning_low: float | None = None,
    critical_low: float | None = None,
    warning_high: float | None = None,
    critical_high: float | None = None,
) -> str:
    """Classify a flow measurement using transparent threshold rules."""

    return classify_threshold(
        flow,
        warning_low=warning_low,
        critical_low=critical_low,
        warning_high=warning_high,
        critical_high=critical_high,
    )


def summarise_status_flags(
    *,
    last_timestamp: pd.Timestamp | str | None = None,
    now: pd.Timestamp | str | None = None,
    battery_voltage: float | int | str | None = None,
    recent_values: Sequence[object] | pd.Series | None = None,
    level: float | int | str | None = None,
    flow: float | int | str | None = None,
    level_warning_low: float | None = None,
    level_critical_low: float | None = None,
    level_warning_high: float | None = None,
    level_critical_high: float | None = None,
    flow_warning_low: float | None = None,
    flow_critical_low: float | None = None,
    flow_warning_high: float | None = None,
    flow_critical_high: float | None = None,
) -> dict[str, str]:
    """Summarise common public-safe sensor QA/QC status flags."""

    flags = {
        "data_delay": classify_data_delay(last_timestamp, now=now),
        "battery": classify_battery_voltage(battery_voltage),
    }

    if recent_values is not None:
        flags["flatline"] = classify_flatline(recent_values)

    if level is not None:
        flags["level"] = classify_level_threshold(
            level,
            warning_low=level_warning_low,
            critical_low=level_critical_low,
            warning_high=level_warning_high,
            critical_high=level_critical_high,
        )

    if flow is not None:
        flags["flow"] = classify_flow_threshold(
            flow,
            warning_low=flow_warning_low,
            critical_low=flow_critical_low,
            warning_high=flow_warning_high,
            critical_high=flow_critical_high,
        )

    return flags


def _to_float(value: float | int | str | None) -> float | None:
    if value is None or pd.isna(value):
        return None

    try:
        numeric = float(str(value).strip().replace(",", "."))
    except ValueError:
        return None

    if pd.isna(numeric):
        return None
    return numeric
