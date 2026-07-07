from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from .core import build_timestamp, find_digital_columns, has_inferable_timestamp
from .io_utils import read_monitoring_csv, sniff_delimiter

SENSITIVE_COLUMN_TOKENS = (
    "lat",
    "lon",
    "link",
    "sim",
    "modem",
    "mname",
    "file_path",
    "path",
    "cliente",
    "commessa",
    "key",
    "id_",
    "id",
    "map",
)

SECRET_FILE_TOKENS = (
    "credential",
    "client_secret",
    "token",
    "password",
    "passwd",
    "secret",
    "apikey",
    "api_key",
)

FOLDER_PURPOSES = {
    "BILANCIO": "Flow-balance / inlet-outlet monitoring table",
    "DATA_3M_POST_PP": "Post-processed 3M/Doppler hydraulic telemetry",
    "DATA_PLUVIO_POST_PP": "Post-processed rainfall / pluviometer telemetry",
    "DATA_PLV_VICINO": "Nearest-rain-gauge reference mapping table",
    "DATA_POST_PP": "Post-processed hydraulic telemetry",
    "DATA_PRE_PP": "Raw or pre-processed hydraulic telemetry",
    "DATA_TEMP": "Temporary mixed telemetry exports",
    "DIARIO_AUTOMATICO": "Automatic asset/data-quality diary report",
    "RENAME": "Rename/header-mapping helper table",
    "INPUT": "Operational input registry/configuration table",
    "PLUVIO": "Rainfall reference table or rainfall matrix",
    "FILE": "Authentication/configuration files used by legacy scripts",
    "TOPO": "Geospatial reference layers",
    "TEMP": "Temporary/generated maps or intermediate outputs",
    "LOGO": "Branding images used in generated reports",
}

DATE_COLUMN_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HOURLY_COLUMN_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[_ T]\d{2}$")


@dataclass(frozen=True)
class CsvAuditProfile:
    """File-level schema/timing profile without exposing row values."""

    relative_path: str
    parent_folder: str
    file_size_bytes: int
    rows: int | None
    columns: int | None
    delimiter: str | None
    dataset_kind: str
    timestamp_layout: str
    valid_timestamps: int | None
    start: str | None
    end: str | None
    median_step_seconds: float | None
    duplicate_timestamps: int | None
    wide_time_columns: int
    wide_time_start: str | None
    wide_time_end: str | None
    digital_columns: str
    sensitive_column_flags: str
    column_names: str
    status: str
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FileInventoryRecord:
    """Public-safe file inventory row."""

    relative_path: str
    parent_folder: str
    extension: str
    file_size_bytes: int
    file_role: str
    risk_flags: str
    publication_recommendation: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def find_csv_files(root: str | Path, *, recursive: bool = True) -> list[Path]:
    root = Path(root)
    pattern = "**/*.csv" if recursive else "*.csv"
    return sorted(path for path in root.glob(pattern) if path.is_file())


def find_files(root: str | Path, *, recursive: bool = True) -> list[Path]:
    root = Path(root)
    pattern = "**/*" if recursive else "*"
    return sorted(path for path in root.glob(pattern) if path.is_file())


def infer_dataset_kind(path: str | Path, columns: list[str]) -> str:
    """Infer a public-safe high-level table type from folder and column names."""

    path = Path(path)
    folder = path.parent.name.upper()
    filename = path.name.upper()
    path_parts = {part.upper() for part in path.parts}
    upper_cols = {str(col).upper() for col in columns}
    joined = " ".join(upper_cols)

    wide = infer_wide_time_columns(columns)
    if "PLUVIO" in path_parts and wide["layout"] == "wide hourly matrix":
        return "rainfall_wide_hourly_matrix"
    if "PLUVIO" in path_parts and wide["layout"] == "wide daily matrix":
        return "rainfall_wide_daily_matrix"

    if filename == "IDRO_APP.CSV":
        return "installation_registry"
    if filename.startswith("INPUT_CONFIGURAZIONE"):
        return "configuration_registry"
    if filename == "LISTA_PUNTI.CSV":
        return "monitoring_point_registry"
    if filename == "RIMUOVERE.CSV":
        return "removal_or_exclusion_table"
    if folder == "DATA_PLV_VICINO":
        return "reference_mapping"
    if folder == "RENAME":
        return "rename_or_header_mapping"
    if "DIARIO" in folder:
        return "asset_status_diary"
    if "BILANCIO" in folder:
        return "balance_timeseries"
    if "PLUVIO" in folder or {"INTENSITA", "CUMULATA"} & upper_cols:
        return "rainfall_timeseries"
    if any(token in joined for token in ("DOPPLER", "PORTATA", "LIVELLO", "VELOCITA")):
        return "hydraulic_timeseries"
    if has_timestamp_columns(columns):
        return "generic_timeseries"
    return "non_timeseries_table"


def has_timestamp_columns(columns: list[str]) -> bool:
    cols = {str(col) for col in columns}
    return "DATAORA" in cols or ({"DATA", "ORA"} <= cols)


def infer_wide_time_columns(columns: list[str]) -> dict[str, object]:
    """Detect rainfall matrices where dates/hours are encoded as column names."""

    date_cols = [str(col) for col in columns if DATE_COLUMN_RE.match(str(col))]
    hourly_cols = [str(col) for col in columns if HOURLY_COLUMN_RE.match(str(col))]

    if hourly_cols:
        return {
            "layout": "wide hourly matrix",
            "count": len(hourly_cols),
            "start": min(hourly_cols),
            "end": max(hourly_cols),
        }
    if date_cols:
        return {
            "layout": "wide daily matrix",
            "count": len(date_cols),
            "start": min(date_cols),
            "end": max(date_cols),
        }
    return {"layout": "none", "count": 0, "start": None, "end": None}


def infer_timestamp_layout(columns: list[str]) -> str:
    cols = {str(col) for col in columns}
    if "DATAORA" in cols:
        return "single DATAORA column"
    if {"DATA", "ORA"} <= cols:
        return "split DATA + ORA columns"
    wide = infer_wide_time_columns(columns)
    if wide["layout"] != "none":
        return str(wide["layout"])
    return "no standard timestamp columns"


def sensitive_column_flags(columns: list[str]) -> list[str]:
    flagged = []
    for col in columns:
        lower = str(col).lower()
        if any(token in lower for token in SENSITIVE_COLUMN_TOKENS):
            flagged.append(str(col))
    return flagged


def audit_csv_file(path: str | Path, *, root: str | Path | None = None) -> CsvAuditProfile:
    """Profile one CSV file without recording any cell values."""

    path = Path(path)
    root_path = Path(root) if root is not None else path.parent
    relative = str(path.relative_to(root_path)) if path.is_relative_to(root_path) else path.name

    try:
        delimiter = sniff_delimiter(path)
        df = read_monitoring_csv(path, sep=delimiter)
        columns = [str(col) for col in df.columns]
        kind = infer_dataset_kind(path, columns)
        layout = infer_timestamp_layout(columns)
        wide = infer_wide_time_columns(columns)
        digital = find_digital_columns(df)
        flagged = sensitive_column_flags(columns)

        valid_ts: int | None = None
        start: str | None = None
        end: str | None = None
        median_step: float | None = None
        duplicates: int | None = None
        status = "ok"

        if has_inferable_timestamp(df):
            ts = build_timestamp(df).dropna().sort_values()
            valid_ts = int(len(ts))
            duplicates = int(ts.duplicated().sum())
            if ts.empty:
                status = "no_valid_timestamps"
            else:
                start = ts.iloc[0].isoformat()
                end = ts.iloc[-1].isoformat()
                diffs = ts.drop_duplicates().diff().dropna().dt.total_seconds()
                median_step = None if diffs.empty else float(diffs.median())
        elif int(wide["count"]):
            status = "wide_time_columns"
            start = str(wide["start"])
            end = str(wide["end"])
        else:
            status = "no_timestamp_columns"

        return CsvAuditProfile(
            relative_path=relative,
            parent_folder=path.parent.name,
            file_size_bytes=path.stat().st_size,
            rows=int(len(df)),
            columns=int(len(columns)),
            delimiter=delimiter,
            dataset_kind=kind,
            timestamp_layout=layout,
            valid_timestamps=valid_ts,
            start=start,
            end=end,
            median_step_seconds=median_step,
            duplicate_timestamps=duplicates,
            wide_time_columns=int(wide["count"]),
            wide_time_start=None if wide["start"] is None else str(wide["start"]),
            wide_time_end=None if wide["end"] is None else str(wide["end"]),
            digital_columns="; ".join(digital),
            sensitive_column_flags="; ".join(flagged),
            column_names="; ".join(columns),
            status=status,
        )
    except Exception as exc:  # pragma: no cover - defensive path for private data audits
        return CsvAuditProfile(
            relative_path=relative,
            parent_folder=path.parent.name,
            file_size_bytes=path.stat().st_size if path.exists() else 0,
            rows=None,
            columns=None,
            delimiter=None,
            dataset_kind="unknown",
            timestamp_layout="unknown",
            valid_timestamps=None,
            start=None,
            end=None,
            median_step_seconds=None,
            duplicate_timestamps=None,
            wide_time_columns=0,
            wide_time_start=None,
            wide_time_end=None,
            digital_columns="",
            sensitive_column_flags="",
            column_names="",
            status="read_error",
            error=f"{type(exc).__name__}: {exc}",
        )


def audit_file(path: str | Path, *, root: str | Path) -> FileInventoryRecord:
    """Create a conservative public-safety inventory record for any file."""

    path = Path(path)
    root_path = Path(root)
    relative = str(path.relative_to(root_path)) if path.is_relative_to(root_path) else path.name
    lower = relative.lower()
    parent = path.parent.name
    suffix = path.suffix.lower() if path.suffix else "[no extension]"

    flags: list[str] = []
    role = "unclassified_file"
    recommendation = "review_manually_before_publication"

    if any(token in lower for token in SECRET_FILE_TOKENS) or suffix in {".pickle", ".pkl"}:
        role = "secret_or_authentication_artifact"
        flags.append("credential_or_token")
        recommendation = "do_not_publish"
    elif "/temp/" in lower.replace("\\", "/") or suffix in {".html", ".png", ".jpg", ".jpeg"}:
        role = "generated_or_visual_output"
        flags.append("generated_output")
        recommendation = "keep_private_or_regenerate_from_synthetic_data"
    elif lower.replace("\\", "/").startswith("topo/") or "/topo/" in lower.replace("\\", "/") or "geojson" in lower:
        role = "geospatial_reference_layer"
        flags.append("geospatial_boundary_or_coordinates")
        recommendation = "keep_private_unless_license_and_sensitivity_are_checked"
    elif suffix in {".csv", ".xlsx", ".xls"}:
        role = "operational_input_table"
        flags.append("private_operational_table")
        recommendation = "publish_synthetic_or_anonymised_fixture_only"
    elif "logo" in lower or suffix in {".svg"}:
        role = "branding_asset"
        flags.append("branding_or_third_party_asset")
        recommendation = "review_rights_before_publication"

    return FileInventoryRecord(
        relative_path=relative,
        parent_folder=parent,
        extension=suffix,
        file_size_bytes=path.stat().st_size,
        file_role=role,
        risk_flags="; ".join(flags),
        publication_recommendation=recommendation,
    )


def audit_data_tree(root: str | Path, *, recursive: bool = True) -> pd.DataFrame:
    """Audit all CSV files below a private data folder."""

    root_path = Path(root)
    profiles = [audit_csv_file(path, root=root_path) for path in find_csv_files(root_path, recursive=recursive)]
    return pd.DataFrame([profile.as_dict() for profile in profiles])


def audit_file_tree(root: str | Path, *, recursive: bool = True) -> pd.DataFrame:
    """Inventory all files below a private folder without opening row data."""

    root_path = Path(root)
    records = [audit_file(path, root=root_path) for path in find_files(root_path, recursive=recursive)]
    return pd.DataFrame([record.as_dict() for record in records])


def write_audit_report(root: str | Path, output_folder: str | Path, *, recursive: bool = True) -> dict[str, Path]:
    """Write CSV and Markdown schema reports for a private data folder."""

    root_path = Path(root)
    output = Path(output_folder)
    output.mkdir(parents=True, exist_ok=True)

    audit_df = audit_data_tree(root_path, recursive=recursive)
    audit_csv = output / "private_data_audit.csv"
    audit_df.to_csv(audit_csv, index=False)

    folder_summary = _folder_summary(audit_df)
    summary_csv = output / "folder_summary.csv"
    folder_summary.to_csv(summary_csv, index=False)

    file_inventory = audit_file_tree(root_path, recursive=recursive)
    inventory_csv = output / "all_file_inventory.csv"
    file_inventory.to_csv(inventory_csv, index=False)

    md_path = output / "private_data_audit.md"
    md_path.write_text(
        _build_markdown_report(root_path, audit_df, folder_summary, file_inventory),
        encoding="utf-8",
    )

    return {
        "audit_csv": audit_csv,
        "folder_summary_csv": summary_csv,
        "all_file_inventory_csv": inventory_csv,
        "markdown_report": md_path,
    }


def _folder_summary(audit_df: pd.DataFrame) -> pd.DataFrame:
    if audit_df.empty:
        return pd.DataFrame()
    grouped = (
        audit_df.groupby(["parent_folder", "dataset_kind", "timestamp_layout", "status"], dropna=False)
        .agg(
            files=("relative_path", "count"),
            rows=("rows", "sum"),
            median_step_seconds=(
                "median_step_seconds",
                lambda values: values.dropna().median() if values.notna().any() else None,
            ),
            min_start=("start", "min"),
            max_end=("end", "max"),
            wide_time_columns=("wide_time_columns", "max"),
        )
        .reset_index()
    )
    grouped["known_purpose"] = grouped["parent_folder"].map(FOLDER_PURPOSES).fillna("")
    return grouped


def _file_inventory_summary(file_inventory: pd.DataFrame) -> pd.DataFrame:
    if file_inventory.empty:
        return pd.DataFrame()
    return (
        file_inventory.groupby(["file_role", "publication_recommendation"], dropna=False)
        .agg(files=("relative_path", "count"), total_bytes=("file_size_bytes", "sum"))
        .reset_index()
    )


def _build_markdown_report(
    root: Path,
    audit_df: pd.DataFrame,
    folder_summary: pd.DataFrame,
    file_inventory: pd.DataFrame,
) -> str:
    lines = [
        "# Private data audit",
        "",
        f"Root folder: `{root}`",
        "",
        "This report contains file/schema/timestamp metadata only. It should still be reviewed",
        "before publication because file names and column names can reveal sensitive asset names.",
        "",
        "## CSV/table summary",
        "",
    ]
    if folder_summary.empty:
        lines.append("No CSV files found.")
    else:
        display_cols = [
            "parent_folder",
            "dataset_kind",
            "files",
            "rows",
            "timestamp_layout",
            "wide_time_columns",
            "median_step_seconds",
            "known_purpose",
            "status",
        ]
        lines.append(folder_summary[display_cols].to_markdown(index=False))

    lines += [
        "",
        "## All-file publication-safety summary",
        "",
    ]
    inventory_summary = _file_inventory_summary(file_inventory)
    if inventory_summary.empty:
        lines.append("No files found.")
    else:
        lines.append(inventory_summary.to_markdown(index=False))

    lines += [
        "",
        "## Suggested publication rule",
        "",
        "Keep original operational input/output files private. Publish only synthetic examples or",
        "tiny anonymised fixtures that have been checked manually for site names, coordinates,",
        "links, phone/SIM identifiers, credentials, client names, and absolute paths.",
        "",
    ]
    if not file_inventory.empty:
        do_not_publish = file_inventory[
            file_inventory["publication_recommendation"].astype(str).eq("do_not_publish")
        ]
        lines += ["## Files that should not be published", ""]
        if do_not_publish.empty:
            lines.append("No credential/token-like files were detected by filename.")
        else:
            lines.append(
                do_not_publish[
                    ["relative_path", "file_role", "risk_flags", "publication_recommendation"]
                ].to_markdown(index=False)
            )

    if not audit_df.empty:
        sensitive = audit_df[audit_df["sensitive_column_flags"].astype(str).str.len() > 0]
        lines += ["", "## CSV files with sensitive-looking column names", ""]
        if sensitive.empty:
            lines.append("No sensitive-looking column names were detected by the simple rule set.")
        else:
            lines.append(
                sensitive[["relative_path", "dataset_kind", "sensitive_column_flags"]]
                .to_markdown(index=False)
            )
    return "\n".join(lines) + "\n"
