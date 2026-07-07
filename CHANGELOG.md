# Changelog

## 0.3.0 - Private INPUT audit support

- Added all-file inventory output to the private audit command.
- Added detection of credential/token-like files, generated visual outputs, geospatial reference layers, and private operational input tables.
- Added recognition of private `INPUT/` registries and wide rainfall matrices where dates or hours are encoded as column names.
- Added `docs/private_input_workflow.md` and stronger `.gitignore` rules for private PVS folders.


## 0.2.0

- Validated the public package against a small private, non-published sample of the original `DATA/` folder.
- Added recursive private-data audit command for mixed nested folders.
- Added dataset-kind inference for hydraulic telemetry, rainfall telemetry, balance tables, asset-status diaries, mappings, and rename/helper files.
- Added robust parsing for both `DATAORA` and split `DATA`/`ORA` timestamps.
- Added flexible CSV delimiter detection and UTF-8 BOM-compatible reading.
- Updated report workflow so non-time-series files are inventoried and skipped instead of crashing.
- Added `tools/make_private_sample.py` to create review samples while avoiding nested duplicate sample folders.
- Added `docs/private_data_workflow.md` and `PRIVATE_SAMPLE_REVIEW.md`.

## 0.1.0

- Initial public-safe repository conversion.
- Added tested telemetry QA/QC package.
- Added synthetic data generator and CLI report workflow.
- Added sanitized legacy script archive and migration/security documentation.

## Final portfolio-ready update

- Added optional applied-AI sensor-health screening utilities.
- Added synthetic anomaly-screening example.
- Added tests for feature extraction and robust anomaly scoring.
- Added documentation for the applied-AI extension.

## Public-clean v2

- Fixed numeric conversion for pandas 3 string dtypes.
- Removed local cache folders from the public-clean package.

## Public-clean v3

- Added `matplotlib` to public dependencies because the optional applied-AI demo writes a PNG diagnostic plot.
- Fixed Ruff import-order/style issues in the ML demo and tests.
