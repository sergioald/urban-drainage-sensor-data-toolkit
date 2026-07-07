# Research software card

## Project name

Urban Drainage Sensor Data Toolkit

## Purpose

Public-safe telemetry QA/QC, private-folder auditing, and reporting utilities for urban drainage and water-network monitoring data.

## Users

- Engineering-data analysts
- Research software reviewers
- Hydrology / urban drainage researchers
- Portfolio reviewers interested in applied sensor-data workflows

## Inputs

CSV files with timestamp information stored either as a combined `DATAORA` column or as separate `DATA` and `ORA` columns. Synthetic examples are included. Private operational files are not included.

The audit workflow can also inventory non-time-series tables, such as mapping/reference files and rename/helper files, without attempting to process them as telemetry.

## Outputs

- Private-folder schema/timing audit CSV
- Folder summary CSV
- Cleaned CSV files, optionally disabled for large/private runs
- Daily aggregate CSV files
- Column profile CSV files
- Per-file summary CSV
- Browser-readable HTML report

## Validation status

The public package includes unit tests for timestamp cleaning, duplicate handling, digital-event forward filling, last-contact status, daily aggregation, recursive folder auditing, non-time-series skip logic, and CLI execution.

A small private validation sample was used to check compatibility with the original `DATA/` folder structure, but the private files are not included in the repository.

## Confidentiality boundary

The repository removes or redacts credentials, IP addresses, email addresses, Google spreadsheet identifiers, logs, binaries, backup files, private CSV exports, and old removal folders.

Private audit outputs avoid row values, but file names and column names can still be sensitive. They should be reviewed manually before sharing.

## Main limitations

- No live connections to private FTP, SCADA, email, Google Sheets, or database services.
- Sanitized legacy scripts are retained for traceability but are not expected to run as-is.
- Synthetic data imitate structure only; they are not calibration or validation datasets.
- The QA/QC routines are screening tools and do not replace engineering review.

## Maintenance status

Prototype repository conversion. Recommended future work is listed in `docs/private_data_workflow.md`.
