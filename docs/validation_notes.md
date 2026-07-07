# Validation notes

This document summarises what has been validated in the public-safe urban drainage sensor-data toolkit, how the examples should be interpreted, and what is intentionally outside the scope of validation.

The repository is designed as a reproducible public demonstration of sensor-data QA/QC, synthetic monitoring workflows, event analytics, dashboard-style outputs, and optional anomaly screening. It is not a production monitoring system and it is not a calibrated hydraulic model.

---

## Validation scope

The validation focuses on four areas:

1. **Software correctness for public utilities**
   - timestamp parsing
   - duplicate timestamp handling
   - invalid timestamp removal
   - numeric conversion
   - missing-row estimates
   - report generation
   - synthetic data generation
   - CLI commands
   - map and network-demo output generation

2. **Public-safe workflow reproduction**
   - replacement of real operational inputs with synthetic examples
   - exclusion of private telemetry, credentials, coordinates, and client/project identifiers
   - generation of synthetic monitoring-point maps and reports

3. **Transparent QA/QC and status rules**
   - stale-data checks
   - battery-status checks
   - flatline detection
   - simple level and flow threshold checks
   - compact status summaries

4. **Demonstration-level analytics**
   - rainfall-event detection
   - level/flow response summaries
   - rainfall-level-flow plot generation
   - optional robust anomaly scoring on synthetic telemetry

---

## What the automated tests check

The automated tests are intended to confirm that the public package behaves consistently and that the main workflows do not break.

They check:

- core cleaning functions preserve valid records and remove or handle invalid timestamps correctly
- duplicated timestamps are detected and handled consistently
- synthetic telemetry can be generated reproducibly
- private-folder audit helpers write summary outputs without publishing row-level data
- report generation writes expected CSV, HTML, and plot outputs
- the anomaly-screening utilities create feature and anomaly-score outputs on synthetic data
- synthetic map generation writes a public-safe HTML map and point table
- string-like boolean values in map flags are interpreted safely
- status-rule helpers classify stale data, low battery, flatlines, and thresholds
- rainfall-event detection groups wet periods into events
- hydraulic-response helpers compute simple event-response metrics
- the synthetic network generator works for short test windows and the full demo window
- the `network-demo` CLI writes the expected report, summary tables, plot, map, and synthetic data files

The tests validate software behaviour and expected output structure. They do not validate the methods against real operational performance data.

---

## What the synthetic demos prove

The synthetic demos prove that the public workflow can run end to end without private data.

### QA/QC report demo

The basic demo proves that synthetic telemetry can be cleaned, summarised, and written to static report outputs.

It demonstrates:

- synthetic CSV generation
- timestamp cleaning
- duplicate and missing-data summaries
- daily summaries
- HTML/CSV report generation
- report-summary plot generation

### Map demo

The map demo proves that a dashboard-style monitoring map can be generated from fictional monitoring points and synthetic coordinates.

It demonstrates:

- public-safe point metadata
- synthetic coordinates
- status markers
- QA/QC filter fields
- dashboard-style Leaflet HTML output

It does not prove anything about real sensor locations or real operational map layers. The map is a synthetic mock-up.

### Network demo

The network demo proves that a small synthetic monitoring network can be processed end to end.

It demonstrates:

- synthetic rainfall, level, flow, and battery telemetry
- rainfall-event detection
- level and flow response summaries
- status-rule checks
- rainfall/level/flow plotting
- synthetic dashboard-map output
- static HTML report generation

It is useful as a public demonstration of workflow design, but it is not a calibrated hydrological or hydraulic simulation.

### Applied-AI anomaly-screening demo

The anomaly-screening demo proves that cleaned synthetic telemetry can be converted into simple sensor-health features and robust anomaly scores.

It demonstrates:

- missing-data features
- rolling statistics
- rate-of-change features
- spike indicators
- flatline indicators
- robust baseline anomaly scoring

It should be interpreted as an explainable screening example, not as a validated production anomaly-detection model.

---

## Role of private samples

The original private material was used only to understand the structure and intent of the legacy workflow. It helped identify the public-safe workflow categories that should be represented synthetically, such as:

- input telemetry folders
- report tables
- map-style monitoring outputs
- curve and plotting outputs
- status and alarm-style checks
- battery and last-contact checks
- operational dashboard patterns

Private samples were not copied into the public repository. Real telemetry, coordinates, operational point IDs, client names, project names, credentials, tokens, and generated private reports are intentionally excluded.

The public implementation recreates workflow patterns using synthetic data and fictional metadata.

---

## What is not validated

The repository does not validate:

- real operational telemetry quality
- real sensor calibration
- real site-specific thresholds
- real rainfall-runoff behaviour
- real hydraulic model performance
- real asset locations
- real map layers
- production anomaly-detection performance
- long-term operational reliability
- deployment to a live monitoring environment

The synthetic examples are designed for public software demonstration and review. They are not a substitute for site-specific engineering validation.

---

## Interpretation guidance for reviewers

Reviewers should interpret this repository as a public-safe research software and portfolio project.

The strongest evidence provided by the repo is:

- clean Python package structure
- reproducible command-line workflows
- automated tests
- CI-ready validation
- public-safe synthetic examples
- clear privacy boundaries
- transparent QA/QC and status-rule logic
- end-to-end demonstration of monitoring data processing

Reviewers should not interpret the repository as:

- a production drainage monitoring platform
- a calibrated hydraulic model
- a validated anomaly-detection product
- a source of real operational data
- a replacement for engineering judgement

---

## Recommended validation commands

Run the full public validation sequence from the repository root:

```bash
python -m pytest -q
urban-drainage-qaqc demo
urban-drainage-qaqc map-demo
urban-drainage-qaqc network-demo
python examples/ml/run_anomaly_demo.py
python examples/network_demo/run_network_demo.py
ruff check .
```

Expected result:

```text
tests pass
QA/QC report generated
synthetic dashboard map generated
synthetic network demo generated
anomaly-screening outputs generated
ruff passes
```

Generated example outputs should normally remain outside version control, usually under:

```text
examples/outputs/
```

---

## Validation position

The validation position of this repository is:

> The software workflow is tested and reproducible on synthetic data. The examples demonstrate public-safe monitoring-data processing patterns. The repository is suitable for portfolio review, software review, and public demonstration, but real-world operational deployment would require separate site-specific validation.

This distinction is intentional. It keeps the project credible while showing the software and engineering workflow clearly.
