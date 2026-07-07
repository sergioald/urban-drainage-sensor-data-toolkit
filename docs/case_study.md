# Public-safe urban drainage telemetry QA/QC and event analytics case study

## Summary

This repository is a public-safe reconstruction of an urban drainage monitoring workflow. It demonstrates how private operational telemetry processing can be converted into reproducible research software without exposing real asset identifiers, client information, coordinates, credentials, or operational records.

The project focuses on a practical engineering question:

> Can urban drainage telemetry be trusted enough to support reporting, sensor-health review, event analysis, and applied-AI screening?

The answer is not only a modelling problem. It is first a data-quality, workflow, and software-engineering problem. Monitoring systems often combine mixed CSV exports, rain-gauge data, level and flow telemetry, device-status logs, field metadata, maps, and generated reports. Before those data can support decision-making or machine learning, the data need to be cleaned, audited, summarised, and checked for operational issues such as stale timestamps, missing records, flatlines, low battery, and anomalous sensor behaviour.

This public repository recreates that workflow with synthetic data, tests, command-line tools, documentation, and dashboard-style examples.

---

## Original problem context

Urban drainage monitoring projects often collect data from distributed field sensors. A typical monitoring workflow may include:

- rainfall gauges
- sewer or drainage level sensors
- flow or velocity sensors
- battery and signal-quality telemetry
- FTP or folder-based file arrivals
- SCADA-style CSV exports
- monitoring-point registries
- generated reports
- map-style operational dashboards

In practice, these data are rarely perfectly clean. Common problems include inconsistent timestamp formats, duplicate timestamps, missing records, delayed file arrivals, stale last-contact times, flatlining sensors, low battery values, and mixed file structures. There may also be operational metadata such as real coordinates, point IDs, client names, project names, credentials, tokens, and map layers.

The original private workflow that motivated this repository processed operational monitoring data and produced outputs useful for reporting, QA/QC review, and map-style monitoring. However, the original data and outputs could not be published directly because they contained private operational information.

The purpose of this repository is therefore to preserve the useful engineering-software patterns while removing private content.

---

## Public-safe conversion strategy

The public repository follows a strict conversion strategy:

1. **Remove private operational data.** Real telemetry, project folders, generated reports, maps, coordinates, credentials, tokens, and client-specific metadata are excluded.

2. **Replace real monitoring points with synthetic examples.** The public examples use fictional point identifiers, synthetic coordinates, and generated telemetry.

3. **Preserve workflow structure.** The code keeps the important workflow stages: data ingestion, timestamp cleaning, duplicate handling, missing-data estimates, reporting, status-rule checks, event summaries, synthetic maps, and optional anomaly screening.

4. **Make the software testable.** The repo is structured as a Python package with a command-line interface, tests, examples, and CI-ready validation.

5. **Document boundaries clearly.** The README and docs state that the project is a public-safe prototype, not a production deployment or calibrated hydraulic model.

This approach demonstrates how private engineering workflows can be converted into public research software without leaking sensitive information.

---

## What the toolkit demonstrates

The toolkit demonstrates several practical capabilities that are common in environmental and infrastructure monitoring projects.

### Timestamp and telemetry QA/QC

The core workflow handles:

- timestamp parsing from common telemetry layouts
- split date/time and single datetime columns
- duplicate timestamp detection
- invalid timestamp removal
- conservative numeric conversion
- missing-row estimates
- daily aggregation
- static HTML/CSV reports
- private-folder audits without row values

These checks are intentionally simple and transparent. They are the type of first-pass QA/QC that is needed before downstream analytics or modelling.

### Public-safe folder auditing

The audit utilities inspect private folders without publishing row-level values. They summarise file structure, CSV schemas, timestamp layouts, sensitive-looking column names, and publication-risk categories.

This is important because privacy risk is not limited to cell values. File names, column names, paths, map layers, and metadata can also reveal sensitive information.

### Sensor status rules

The repository includes transparent sensor-health rules for:

- stale data / delayed last contact
- battery voltage status
- flatline detection
- level thresholds
- flow thresholds
- compact status summaries

These rules are deliberately explainable. They are not presented as universal operational thresholds. Real deployments would require site-specific validation and engineering agreement.

### Synthetic dashboard map

The synthetic map output recreates the structure of a monitoring dashboard while avoiding private information. It includes:

- fictional monitoring points
- synthetic coordinates
- status markers
- QA/QC filters
- layer controls
- search behaviour
- synthetic region overlays

The goal is to show the software and dashboard pattern, not to publish any real operational map.

### Optional applied-AI anomaly screening

The applied-AI component converts cleaned synthetic telemetry into simple sensor-health features and robust anomaly scores. It is intentionally lightweight and transparent. For a public QA/QC repository, explainability and reproducibility are more important than claiming production ML performance.

The anomaly screening should be interpreted as a demonstration of how cleaned telemetry can feed applied-AI workflows, not as a validated anomaly-detection model.

---

## Synthetic network demo

The Phase 2 network demo extends the repository from a QA/QC utility into a small end-to-end monitoring demonstrator.

The synthetic network contains:

- one rainfall gauge
- two level sensors
- one flow sensor
- battery/status telemetry
- synthetic monitoring-point metadata
- generated data-quality issues

The workflow is:

```text
synthetic rainfall + sensor telemetry
        ↓
QA/QC cleaning and status rules
        ↓
rainfall-event detection
        ↓
level/flow response summaries
        ↓
rainfall-level-flow plot
        ↓
HTML report
        ↓
synthetic dashboard map
```

The network demo produces outputs such as:

```text
examples/outputs/network_demo/
├── report.html
├── network_summary.csv
├── event_summary.csv
├── sensor_response_summary.csv
├── status_summary.csv
├── rainfall_level_flow.png
├── synthetic_monitoring_points.html
└── data/
```

This makes the repository more representative of a real monitoring workflow while remaining safe for public release.

---

## Event analytics

The rainfall-event detection is intentionally simple:

- rainfall records greater than zero are treated as wet records
- wet records separated by more than a configurable dry gap start a new event
- small events below a minimum rainfall depth can be discarded
- each event is summarised by start time, end time, duration, total rainfall, peak interval rainfall, and number of wet records

The sensor-response functions then summarise level and flow behaviour around each event:

- start value
- mean value
- peak value
- minimum value
- samples in the response window
- time to peak

This is not a full hydrodynamic model. It is a transparent event-screening workflow that can support monitoring review and identify periods that deserve closer engineering inspection.

---

## Engineering judgement shown

This project is not only about writing Python functions. It demonstrates engineering-software judgement in several ways:

1. **Privacy-first publication.** The repository avoids publishing real operational data, maps, coordinates, credentials, or client identifiers.

2. **Workflow preservation.** The public code preserves the logic of the original workflow without exposing its private content.

3. **Transparent methods.** QA/QC, status rules, event detection, and anomaly screening are implemented in simple, inspectable ways.

4. **Reproducibility.** The workflow can be run from the command line and validated with automated tests.

5. **Portfolio relevance.** The repository links environmental monitoring, sensor-data QA/QC, automated reporting, synthetic dashboards, event analytics, and applied AI.

6. **Appropriate limitations.** The project avoids overclaiming. It does not present synthetic demonstrations as production monitoring or calibrated hydraulic modelling.

---

## How this relates to applied AI and predictive monitoring

Applied AI in infrastructure monitoring often fails when the data foundation is weak. Before advanced models are useful, the system needs:

- reliable timestamp parsing
- consistent sampling assumptions
- missing-data checks
- duplicate detection
- stale-data detection
- sensor-health flags
- interpretable baseline metrics
- event context
- reproducible reports

This repository demonstrates that foundation. It shows how telemetry can be cleaned, structured, checked, and summarised before optional anomaly screening is applied.

That is directly relevant to predictive maintenance, environmental monitoring, drainage monitoring, structural monitoring, and digital-twin workflows.

---

## Limitations

This repository is a public-safe demonstrator. It has important limitations:

- all public data are synthetic
- coordinates and monitoring-point IDs are fictional
- status thresholds are illustrative
- rainfall-event logic is simplified
- the dashboard map is a synthetic mock-up
- the anomaly-screening model is not production validated
- the workflow is not a calibrated hydraulic model
- real deployments require site-specific thresholds, validation, data governance, and engineering review

These limitations are intentional. The repository prioritises reproducibility, safety, transparency, and reviewability.

---

## How to run the main demonstrations

Install the package in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Run the basic QA/QC report:

```bash
urban-drainage-qaqc demo
```

Run the synthetic dashboard map:

```bash
urban-drainage-qaqc map-demo
```

Run the synthetic network demo:

```bash
urban-drainage-qaqc network-demo
```

Run tests and linting:

```bash
python -m pytest -q
ruff check .
```

---

## Portfolio value

This repository demonstrates how messy operational engineering workflows can be converted into clean, tested, public-safe Python software. It combines:

- sensor-data QA/QC
- urban drainage monitoring
- automated reporting
- rainfall-event analytics
- simple hydraulic response summaries
- status-rule logic
- dashboard-style visualisation
- optional anomaly screening
- privacy-aware research software practice

The result is a compact but realistic example of applied engineering data science: not only building models, but building the trustworthy data workflow that models depend on.
