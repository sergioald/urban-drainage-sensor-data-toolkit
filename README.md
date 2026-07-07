# Urban Drainage Sensor Data Toolkit

![Tests](https://img.shields.io/badge/tests-pytest-informational)
![Python](https://img.shields.io/badge/Python-3.10%2B-informational?logo=python)
![Status](https://img.shields.io/badge/status-public--safe%20prototype-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Public-safe Python toolkit for urban drainage and water-network telemetry QA/QC, automated reporting, and optional applied-AI anomaly screening.

The repository demonstrates how private operational monitoring workflows can be converted into a clean research-software package using synthetic examples, tests, documentation, and strict publication boundaries.

> Status: prototype / repository conversion.  
> The package is suitable for public demonstration and software review. It is not a drop-in replacement for the original operational system.

---

## What this repository demonstrates

| Area | What is demonstrated |
|---|---|
| Engineering data QA/QC | Timestamp parsing, duplicate handling, missing-row estimates, digital-event forward filling, mixed-folder audits |
| Urban hydrology monitoring | Flow, level, velocity, rainfall, battery, and last-contact style telemetry checks |
| Research software | `src/` package structure, CLI, tests, docs, examples, and clear limitations |
| Public-safe release | Synthetic data and private-data guidance instead of real monitoring records |
| Optional applied AI | Explainable sensor-health features and robust anomaly scoring on synthetic telemetry |

---

## Workflow overview

```text
Private telemetry structure
        │
        ├── local private audit, never committed
        ├── schema/quality checks
        └── reusable public-safe utilities
                ↓
Synthetic telemetry CSVs → cleaning/QA/QC → daily summaries → CSV + HTML report
                ↓
Optional sensor-health features → robust anomaly scores → diagnostic plot
```

---

## Quick start with Anaconda

```powershell
conda create -n urban-drainage-qaqc python=3.11 -y
conda activate urban-drainage-qaqc

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
```

Run the public demo:

```powershell
urban-drainage-qaqc demo
```

Run the optional applied-AI demo:

```powershell
python examples/ml/run_anomaly_demo.py
```

---

## Command-line usage

Create synthetic data:

```bash
urban-drainage-qaqc create-synthetic --output examples/data/synthetic_monitoring_point.csv
```

Run QA/QC over the synthetic example folder:

```bash
urban-drainage-qaqc run --input examples/data --output examples/outputs/synthetic_report
```

Audit a private local folder without publishing row values:

```bash
urban-drainage-qaqc audit --input "path/to/private/folder" --output "private_audit"
```

Keep private audit outputs outside Git or in ignored folders.

---

## Optional applied-AI extension

The toolkit includes a lightweight applied-AI example for sensor-health screening. It uses synthetic telemetry only and demonstrates transparent anomaly scoring for:

- missing data
- spikes
- flat-line behaviour
- signal-quality degradation
- basic sensor-health drift

Run it with:

```bash
python examples/ml/run_anomaly_demo.py
```

The example writes anomaly scores, a compact health summary, and a diagnostic plot to:

```text
examples/outputs/ml_anomaly_demo/
```

This is intentionally presented as an explainable baseline, not as a validated production ML model.

---

## Repository structure

```text
.
├── .github/workflows/          # CI checks
├── docs/                       # Public documentation
├── examples/                   # Synthetic data and demos
├── scripts/                    # Helper scripts
├── src/urban_drainage_sensor_toolkit/
│   ├── cli.py                  # Command-line interface
│   ├── io.py                   # Input/output helpers
│   ├── cleaning.py             # Cleaning and timestamp handling
│   ├── audit.py                # Private-folder audit helpers
│   ├── reporting.py            # Report generation
│   └── ml/                     # Optional sensor-health anomaly screening
├── tests/                      # Public tests
├── tools/                      # Private sampling helpers
├── pyproject.toml
├── README.md
└── GITHUB_CREATE_REPO_ANACONDA_GUIDE.md
```

---

## Private-data boundary

Do not commit private operational folders, private samples, credentials, tokens, pickles, maps with real coordinates, or generated private reports.

The `.gitignore` is intentionally strict and excludes common private/local artefacts such as:

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

---

## Limitations

- The public examples are synthetic.
- The applied-AI demo is an explainable baseline, not a validated production model.
- Private operational data should remain outside Git.
- Local private audit results should be reviewed before sharing.

---

## License

MIT License.
