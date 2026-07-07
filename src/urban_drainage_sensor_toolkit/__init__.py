"""Public-safe utilities for urban drainage telemetry CSV QA/QC and reporting."""

from .audit import audit_csv_file, audit_data_tree
from .core import (
    build_timestamp,
    classify_contact,
    clean_timeseries,
    daily_aggregate,
    merge_csv_files,
    summarize_measurement_point,
)
from .io_utils import read_monitoring_csv, sniff_delimiter

__all__ = [
    "audit_csv_file",
    "audit_data_tree",
    "build_timestamp",
    "classify_contact",
    "clean_timeseries",
    "daily_aggregate",
    "merge_csv_files",
    "read_monitoring_csv",
    "sniff_delimiter",
    "summarize_measurement_point",
]

__version__ = "0.2.0"
