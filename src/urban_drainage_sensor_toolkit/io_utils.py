from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

COMMON_DELIMITERS = (";", ",", "\t", "|")


def sniff_delimiter(path: str | Path, *, encoding: str = "utf-8-sig", sample_bytes: int = 8192) -> str:
    """Infer the delimiter used by a CSV-like monitoring export.

    Most legacy files use semicolon separators, but this small helper makes the
    public package safer to use on folders that contain mixed CSV exports.
    """

    path = Path(path)
    text = path.read_bytes()[:sample_bytes].decode(encoding, errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text, delimiters="".join(COMMON_DELIMITERS))
        return dialect.delimiter
    except csv.Error:
        counts = {delimiter: text.count(delimiter) for delimiter in COMMON_DELIMITERS}
        return max(counts, key=counts.get) if any(counts.values()) else ";"


def read_monitoring_csv(
    path: str | Path,
    *,
    sep: str | None = None,
    encoding: str = "utf-8-sig",
    dtype: Any = None,
    low_memory: bool = False,
    **kwargs: Any,
) -> pd.DataFrame:
    """Read a monitoring CSV with conservative defaults.

    Parameters are intentionally close to :func:`pandas.read_csv`. The default
    encoding handles UTF-8 files with or without a byte-order mark. If ``sep`` is
    omitted, the delimiter is inferred from the first bytes of the file.
    """

    path = Path(path)
    delimiter = sep or sniff_delimiter(path, encoding=encoding)
    return pd.read_csv(
        path,
        sep=delimiter,
        encoding=encoding,
        dtype=dtype,
        low_memory=low_memory,
        **kwargs,
    )
