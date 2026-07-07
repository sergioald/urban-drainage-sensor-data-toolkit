# Live demo

## Live app

[Open the live Streamlit demo](https://urban-drainage-sensor-data-toolkit.streamlit.app/)

This repository includes a lightweight Streamlit demo for the synthetic urban drainage monitoring workflow.

The demo is intended for recruiters, collaborators, and reviewers who want to understand the project without cloning the repository or setting up a local Python environment.

## What the demo shows

The live app runs the synthetic network workflow:

```text
synthetic rainfall + level + flow telemetry
        ↓
rainfall-event detection
        ↓
sensor response summaries
        ↓
status-rule checks
        ↓
rainfall/level/flow plot
        ↓
synthetic dashboard map
        ↓
downloadable CSV/HTML outputs
```

## Public-safety boundary

The live demo uses synthetic data only.

It does not include:

- real telemetry
- real coordinates
- real monitoring point IDs
- client names
- project names
- credentials
- tokens
- private reports

## What the demo proves

The live demo proves that the public workflow can run end to end in a browser.

It demonstrates:

- reproducible synthetic data generation
- rainfall-event analytics
- simple hydraulic response summaries
- status-rule outputs
- dashboard-style map generation
- automated report outputs
- downloadable CSV and HTML outputs

## What the demo does not prove

The live demo does not validate:

- real operational sensor performance
- calibrated hydraulic behaviour
- production anomaly-detection performance
- site-specific thresholds
- live monitoring deployment

## Local run

From the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

or, in an editable development environment:

```bash
python -m pip install -e ".[dev]"
python -m pip install streamlit
streamlit run app.py
```

## Deployment target

The recommended deployment target is Streamlit Community Cloud because it can deploy directly from a GitHub repository.

Use:

```text
app.py
```

as the app entry point.

After deployment, add the public URL to the README live-demo section.
