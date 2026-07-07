# Validation scope

## What is tested

The current tests validate public package behaviour on synthetic and tiny public-safe fixtures:

- parsing timestamps from `DATAORA` columns;
- parsing split `DATA` and `ORA` columns;
- dropping invalid timestamp rows;
- sorting and de-duplicating timestamps;
- forward-filling digital/event columns;
- estimating missing rows from expected time steps;
- daily aggregation of rainfall-like and continuous variables;
- recursive folder audits for mixed private-style `DATA/` trees;
- skipping non-time-series mapping tables without failing the report workflow;
- CLI demo, audit, and report execution.

## Private sample validation

A small private sample of the original operational folder structure was used locally to check schema compatibility. The sample itself is not included in the repository. The review confirmed support for:

- semicolon-separated CSV exports;
- UTF-8 BOM-compatible files;
- `DATAORA` timestamps;
- split `DATA` + `ORA` timestamps;
- 6-minute hydraulic/balance telemetry;
- 1-minute rainfall/temp telemetry;
- non-time-series helper/mapping tables;
- irregular automatic diary/status reports.

## What is not tested

- Real FTP, SCADA, email, Google Sheets, or database connections.
- Full private operational history.
- Original private monitoring data as committed test fixtures.
- Hydrological correctness of derived metrics beyond simple QA/QC summaries.
- Windows-only GUI or automation behaviour.
- Operational alert thresholds from the original deployment environment.

## Interpretation

Passing tests means the public-safe toolkit behaves consistently for the supported synthetic and schema-level CSV workflows. It does not prove that the historical operational system can be redeployed without its private environment.
