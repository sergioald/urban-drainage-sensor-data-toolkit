# Private INPUT folder workflow

The legacy PVS workflow uses an `INPUT/` folder for operational registries,
configuration tables, rainfall matrices, geospatial reference layers, logos, and
authentication artifacts. The public repository should not include the original
`INPUT/` folder.

## What the private INPUT sample showed

The private sample contained these high-level categories:

| Area | Purpose | Public handling |
|---|---|---|
| `INPUT/*.csv` and `INPUT.xlsx` | Operational registries, point lists, configuration tables, exclusion/removal lists | Keep private; publish only synthetic or anonymised templates |
| `INPUT/PLUVIO/*.csv` | Wide rainfall matrices with dates/hours encoded as columns | Keep private; publish only tiny synthetic examples |
| `INPUT/FILE/*credentials*.json` and `*token*.pickle` | Authentication artifacts used by legacy scripts | Never publish; rotate credentials if they were exposed |
| `INPUT/TOPO/` | Geospatial boundary/reference layers | Keep private unless licence and location sensitivity are checked |
| `INPUT/TEMP/HTML` and `INPUT/TEMP/PNG` | Generated maps/intermediate visual outputs | Do not use as fixtures; regenerate from synthetic data if needed |
| `INPUT/LOGO/` | Branding/report assets | Check rights before publication |

## Recommended public approach

Use the repository to document the structure and behaviour, not to publish the
real operational inputs. Good public substitutes are:

1. synthetic configuration tables with generic clients/projects,
2. synthetic rainfall matrices with 2-3 monitoring points and a few date/hour columns,
3. synthetic telemetry CSVs with generic sensor names,
4. small generated example reports created entirely from synthetic inputs.

## Audit command

Run this locally against the private input folder:

```bash
urban-drainage-qaqc audit --input "path/to/private/PVS/INPUT" --output "private_input_audit"
```

The audit writes:

- `private_data_audit.csv` for CSV schema/timestamp metadata,
- `folder_summary.csv` for table-level summaries,
- `all_file_inventory.csv` for all files, including non-CSV files,
- `private_data_audit.md` for a human-readable report.

The audit intentionally avoids recording row values. It still needs manual review
because file names and column names can reveal private asset information.

## Git safety

Do not commit these folders or files:

```text
INPUT/
DATA/
REPORT/
OUTPUT/
*credentials*.json
*token*.pickle
*client_secret*.json
```

The repository `.gitignore` includes these patterns, but you should still run a
secret scan before publishing.
