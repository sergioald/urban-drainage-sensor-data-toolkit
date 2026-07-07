# Public-clean package audit

Generated for `urban-drainage-sensor-data-toolkit-public-clean.zip`.

## Removed before packaging

The clean package removes or excludes private/local artefacts matching:

```text
INPUT/
DATA/
REPORT/
OUTPUT/
PRIVATE_SAMPLE*/
private_audit*/
private_report*/
credentials.json
*token*
*.pickle
*.pkl
TOPO/
TEMP/
```

It also removes the raw legacy-script archive and legacy migration inventory to keep this public package focused and lower risk.

## Removed paths

```text
PRIVATE_SAMPLE_REVIEW.md
REPO_CONVERSION_REPORT.md
docs/legacy_inventory.csv
docs/legacy_migration_notes.md
legacy_scripts
```

## Final scan result

Blocked paths remaining in the package:

```text
None.
```

Total files in clean package before zipping: `65`.

## Note

Synthetic examples under `examples/data/` and `examples/outputs/` are intentionally kept because they are required for the public demo.
