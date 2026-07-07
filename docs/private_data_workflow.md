# Private data validation workflow

The repository must not include the original operational input/output files. The private samples were useful to improve the public code because they confirmed that the operational `DATA/` folder is not one single CSV format. It contains several related table types.

## Observed private-folder structure

| Folder | Interpreted role | Timestamp layout | Typical interval | Public-release advice |
|---|---|---:|---:|---|
| `BILANCIO` | Flow-balance / inlet-outlet monitoring table | `DATAORA` | 6 min | Keep private; reproduce with synthetic data only. |
| `DATA_3M_POST_PP` | Post-processed 3M/Doppler hydraulic telemetry | `DATAORA` | 6 min | Good candidate for synthetic examples. |
| `DATA_PLUVIO_POST_PP` | Post-processed rainfall / pluviometer telemetry | `DATAORA` | 1 min | Good candidate for synthetic rainfall fixtures. |
| `DATA_PLV_VICINO` | Nearest-rain-gauge reference mapping | no time column | n/a | Keep private because names/asset references may identify sites. |
| `DATA_POST_PP` | Post-processed hydraulic telemetry | `DATAORA` | 6 min | Good candidate for synthetic examples. |
| `DATA_PRE_PP` | Raw/pre-processed hydraulic telemetry | `DATA` + `ORA` | 6 min | Useful for tests because it exercises split date/time parsing. |
| `DATA_TEMP` | Temporary mixed telemetry exports | `DATA` + `ORA` | mixed, often 1 min | Keep private; use only synthetic equivalents. |
| `DIARIO_AUTOMATICO` | Automatic asset/data-quality diary | `DATAORA` | irregular | Keep private; likely contains links, coordinates, identifiers, and operational notes. |
| `RENAME` | Rename/header-mapping helper | mixed/no valid time series | n/a | Keep private; useful only as schema/migration context. |

## What changed in the public repository after checking the samples

- Added recursive folder audits for mixed `DATA/` trees.
- Added schema/type detection for telemetry, rainfall, balance, diary, mapping, and rename/helper tables.
- Added robust timestamp parsing for both `DATAORA` and split `DATA`/`ORA` formats.
- Added safer CSV reading with delimiter detection and UTF-8 BOM handling.
- Updated the report workflow so non-time-series tables are listed and skipped instead of crashing.
- Added CLI support for private audits:

```bash
urban-drainage-qaqc audit --input "path/to/private/DATA" --output "private_audit"
```

- Added a safer sample-maker script under `tools/` that avoids resampling a previous sample folder:

```bash
python tools/make_private_sample.py --root "path/to/private/DATA" --n 3 --zip
```

## Recommended public/private boundary

Keep private:

- original input/output CSVs;
- station names and monitoring-point names;
- coordinates;
- links and map URLs;
- SIM/modem/device identifiers;
- client names;
- operational diary rows;
- absolute local/network paths;
- credentials, tokens, or endpoint details.

Public-safe:

- synthetic CSVs with the same broad schema;
- tests using generic names such as `Sensor_A`, `Site_001`, and `Run_001`;
- schema documentation without row values;
- high-level methodology and validation notes.

## Why the uploaded validation sample should not be committed

The sample files are still real operational records. Even if the rows are small subsets, they can contain timing, asset-status, identifiers, links, coordinates, or operational behaviour. They should remain outside Git and should not be uploaded to GitHub.
