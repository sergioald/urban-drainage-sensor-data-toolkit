from __future__ import annotations

import warnings
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype

from .io_utils import read_monitoring_csv

DEFAULT_DATETIME_COLUMNS = ("DATAORA", "timestamp", "datetime", "DateTime")
DEFAULT_DATE_COLUMNS = ("DATA", "Data", "date", "Date")
DEFAULT_TIME_COLUMNS = ("ORA", "Ora", "time", "Time")
COMMON_TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%y %H:%M:%S",
    "%d/%m/%y %H:%M",
)


@dataclass(frozen=True)
class TimeseriesSummary:
    """Small QA/QC summary for one sensor or monitoring point."""

    rows: int
    valid_timestamps: int
    start: pd.Timestamp | None
    end: pd.Timestamp | None
    duration_hours: float | None
    median_step_seconds: float | None
    duplicate_timestamps: int
    missing_rows_estimate: int | None
    digital_columns: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "rows": self.rows,
            "valid_timestamps": self.valid_timestamps,
            "start": None if self.start is None else self.start.isoformat(),
            "end": None if self.end is None else self.end.isoformat(),
            "duration_hours": self.duration_hours,
            "median_step_seconds": self.median_step_seconds,
            "duplicate_timestamps": self.duplicate_timestamps,
            "missing_rows_estimate": self.missing_rows_estimate,
            "digital_columns": ", ".join(self.digital_columns),
        }


def _first_existing(columns: Sequence[str], candidates: Sequence[str]) -> str | None:
    existing = {str(c): c for c in columns}
    for candidate in candidates:
        if candidate in existing:
            return existing[candidate]
    return None


def _parse_timestamp_text(values: pd.Series, *, day_first: bool = True) -> pd.Series:
    """Parse timestamp strings while avoiding noisy pandas format warnings."""

    text = values.astype(str).str.strip()
    text = text.mask(text.str.lower().isin({"", "nan", "nat", "none"}))

    best: pd.Series | None = None
    best_valid = -1
    for fmt in COMMON_TIMESTAMP_FORMATS:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        valid = int(parsed.notna().sum())
        if valid > best_valid:
            best = parsed
            best_valid = valid
        if valid == len(text.dropna()):
            return parsed

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        fallback = pd.to_datetime(text, errors="coerce", dayfirst=day_first, format="mixed")

    if best is None:
        return fallback

    # Fill rows parsed by pandas' mixed parser but missed by the best explicit format.
    return best.fillna(fallback)


def build_timestamp(
    df: pd.DataFrame,
    *,
    datetime_col: str | None = None,
    date_col: str | None = None,
    time_col: str | None = None,
    day_first: bool = True,
) -> pd.Series:
    """Return a parsed timestamp series from common Italian/SCADA CSV layouts.

    The legacy scripts use both single ``DATAORA`` columns and split ``DATA`` /
    ``ORA`` columns. The parser supports ISO-style timestamps as well as
    day-first date/time exports, and treats blank rows as invalid timestamps.
    """

    datetime_col = datetime_col or _first_existing(df.columns, DEFAULT_DATETIME_COLUMNS)
    if datetime_col is not None:
        return _parse_timestamp_text(df[datetime_col], day_first=day_first)

    date_col = date_col or _first_existing(df.columns, DEFAULT_DATE_COLUMNS)
    time_col = time_col or _first_existing(df.columns, DEFAULT_TIME_COLUMNS)
    if date_col is None or time_col is None:
        raise ValueError(
            "Could not infer timestamp columns. Provide datetime_col or date_col/time_col."
        )

    combined = df[date_col].astype(str).str.strip() + " " + df[time_col].astype(str).str.strip()
    return _parse_timestamp_text(combined, day_first=day_first)


def has_inferable_timestamp(df: pd.DataFrame) -> bool:
    """Return True when common timestamp columns are present."""

    if _first_existing(df.columns, DEFAULT_DATETIME_COLUMNS) is not None:
        return True
    return (
        _first_existing(df.columns, DEFAULT_DATE_COLUMNS) is not None
        and _first_existing(df.columns, DEFAULT_TIME_COLUMNS) is not None
    )


def clean_timeseries(
    df: pd.DataFrame,
    *,
    datetime_col: str | None = None,
    date_col: str | None = None,
    time_col: str | None = None,
    output_timestamp_col: str = "timestamp",
    digital_keywords: Sequence[str] = ("DIGITAL", "EVENT", "ALLARME", "ALARM"),
    deduplicate: bool = True,
    keep: str = "last",
    numeric_exclusions: Sequence[str] = ("id", "tag", "name", "key", "link", "sim", "lat", "lon"),
) -> pd.DataFrame:
    """Clean a telemetry table for QA/QC and reporting.

    Operations are intentionally conservative: parse timestamps, drop invalid time
    rows, sort, remove duplicate timestamps, forward-fill digital/event columns,
    and convert obvious numeric columns while preserving identifiers and private
    metadata-like fields as strings.
    """

    out = df.copy()
    out[output_timestamp_col] = build_timestamp(
        out,
        datetime_col=datetime_col,
        date_col=date_col,
        time_col=time_col,
    )
    out = out.dropna(subset=[output_timestamp_col]).sort_values(output_timestamp_col)

    if deduplicate:
        out = out.drop_duplicates(subset=[output_timestamp_col], keep=keep)

    digital_cols = find_digital_columns(out, digital_keywords=digital_keywords)
    if digital_cols:
        out.loc[:, digital_cols] = out.loc[:, digital_cols].ffill()

    lower_exclusions = tuple(s.lower() for s in numeric_exclusions)
    for col in out.columns:
        if col == output_timestamp_col or col in digital_cols:
            continue
        name = str(col).lower()
        if any(token in name for token in lower_exclusions):
            continue
        # Pandas 3 may infer text columns as StringDtype instead of object.
        # Convert both object and string-like columns when the values look numeric.
        if is_object_dtype(out[col]) or is_string_dtype(out[col]):
            candidate = pd.to_numeric(
                out[col].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            )
            if candidate.notna().sum() >= max(1, int(0.6 * len(candidate))):
                out[col] = candidate

    return out.reset_index(drop=True)


def find_digital_columns(
    df: pd.DataFrame,
    *,
    digital_keywords: Sequence[str] = ("DIGITAL", "EVENT", "ALLARME", "ALARM"),
) -> list[str]:
    keywords = tuple(k.upper() for k in digital_keywords)
    return [str(col) for col in df.columns if any(k in str(col).upper() for k in keywords)]


def summarize_measurement_point(
    df: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    expected_interval_seconds: float | None = None,
) -> TimeseriesSummary:
    """Compute a small timing/data-availability summary for one cleaned table."""

    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    ts = pd.to_datetime(df[timestamp_col], errors="coerce").dropna().sort_values()
    duplicate_count = int(ts.duplicated().sum())
    digital_cols = tuple(find_digital_columns(df))

    if ts.empty:
        return TimeseriesSummary(
            rows=len(df),
            valid_timestamps=0,
            start=None,
            end=None,
            duration_hours=None,
            median_step_seconds=None,
            duplicate_timestamps=duplicate_count,
            missing_rows_estimate=None,
            digital_columns=digital_cols,
        )

    start = ts.iloc[0]
    end = ts.iloc[-1]
    diffs = ts.diff().dropna().dt.total_seconds()
    median_step = None if diffs.empty else float(diffs.median())
    duration_hours = float((end - start).total_seconds() / 3600.0)

    missing_rows = None
    step = expected_interval_seconds or median_step
    if step and step > 0 and len(ts) > 1:
        expected_rows = int(round((end - start).total_seconds() / step)) + 1
        missing_rows = max(0, expected_rows - len(ts.drop_duplicates()))

    return TimeseriesSummary(
        rows=len(df),
        valid_timestamps=int(len(ts)),
        start=start,
        end=end,
        duration_hours=duration_hours,
        median_step_seconds=median_step,
        duplicate_timestamps=duplicate_count,
        missing_rows_estimate=missing_rows,
        digital_columns=digital_cols,
    )


def classify_contact(
    last_timestamp: pd.Timestamp | str | None,
    *,
    now: pd.Timestamp | str | None = None,
    warning_after_hours: float = 24.0,
    critical_after_hours: float = 72.0,
) -> str:
    """Classify last-contact status for a telemetry point."""

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


def daily_aggregate(
    df: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    value_columns: Sequence[str] | None = None,
    rainfall_keywords: Sequence[str] = ("rain", "piogg", "pluvio", "intensita", "cumulata"),
) -> pd.DataFrame:
    """Create simple daily aggregates for cleaned telemetry tables.

    Rainfall-like columns are summed; other numeric columns are averaged. This is
    not a hydraulic model; it is a public-safe reporting helper.
    """

    if timestamp_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")
    work = df.copy()
    work[timestamp_col] = pd.to_datetime(work[timestamp_col], errors="coerce")
    work = work.dropna(subset=[timestamp_col]).set_index(timestamp_col)

    if value_columns is None:
        value_columns = [c for c in work.columns if pd.api.types.is_numeric_dtype(work[c])]

    aggregations: dict[str, str] = {}
    for col in value_columns:
        lower = str(col).lower()
        aggregations[col] = "sum" if any(k in lower for k in rainfall_keywords) else "mean"

    if not aggregations:
        return pd.DataFrame(columns=["date"])

    out = work.resample("D").agg(aggregations)
    out.index.name = "date"
    return out.reset_index()


def merge_csv_files(
    paths: Iterable[str | Path],
    *,
    sep: str | None = None,
    skiprows: int | Sequence[int] | None = None,
    clean: bool = True,
    source_column: str = "source_file",
) -> pd.DataFrame:
    """Merge multiple telemetry CSV files."""

    frames: list[pd.DataFrame] = []
    for path in paths:
        p = Path(path)
        frame = read_monitoring_csv(p, sep=sep, skiprows=skiprows)
        frame[source_column] = p.name
        frames.append(frame)
    if not frames:
        raise ValueError("No CSV files were provided")
    merged = pd.concat(frames, ignore_index=True, sort=False)
    return clean_timeseries(merged) if clean else merged


def dataframe_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Return a lightweight column profile table for reports."""

    rows = []
    for col in df.columns:
        series = df[col]
        rows.append(
            {
                "column": col,
                "dtype": str(series.dtype),
                "non_null": int(series.notna().sum()),
                "missing": int(series.isna().sum()),
                "unique": int(series.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)
