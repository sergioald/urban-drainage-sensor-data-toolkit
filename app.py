from __future__ import annotations

import base64
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from urban_drainage_sensor_toolkit.network_report import run_synthetic_network_demo  # noqa: E402

st.set_page_config(
    page_title="Urban Drainage Sensor QA/QC Demo",
    page_icon="🌧️",
    layout="wide",
)

st.title("Urban Drainage Sensor Data Toolkit")
st.caption(
    "Public-safe synthetic demo: QA/QC, rainfall-event analytics, "
    "status rules, reporting, dashboard map output, and anomaly-screening context."
)

st.info(
    "This online demo uses synthetic data only. It does not contain real telemetry, "
    "coordinates, client names, project identifiers, credentials, or operational asset IDs."
)

with st.sidebar:
    st.header("Synthetic demo controls")
    periods = st.slider(
        "Records per sensor",
        min_value=96,
        max_value=672,
        value=336,
        step=48,
        help="Each record represents one 30-minute synthetic telemetry interval.",
    )

    st.markdown("### Demo scope")
    st.markdown(
        """
- Synthetic rainfall gauge
- Two synthetic level sensors
- One synthetic flow sensor
- Battery/status telemetry
- Rainfall-event detection
- Level/flow response summaries
- Dashboard-style map output
"""
    )

    run_clicked = st.button("Run synthetic network demo", type="primary")

if run_clicked or "generated" not in st.session_state:
    with st.spinner("Generating synthetic network demo..."):
        temp_dir = Path(tempfile.mkdtemp(prefix="urban_drainage_demo_"))
        generated = run_synthetic_network_demo(temp_dir, periods=periods)
        st.session_state.generated = generated
        st.session_state.output_dir = temp_dir

generated: dict[str, Path] = st.session_state.generated

st.subheader("Synthetic rainfall, level and flow response")
st.image(str(generated["rainfall_level_flow_plot"]), width="stretch")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Network summary")
    network_summary = pd.read_csv(generated["network_summary_csv"])
    st.dataframe(network_summary, width="stretch", hide_index=True)

with col2:
    st.subheader("Status summary")
    status_summary = pd.read_csv(generated["status_summary_csv"])
    st.dataframe(status_summary, width="stretch", hide_index=True)

st.subheader("Rainfall event summary")
event_summary = pd.read_csv(generated["event_summary_csv"])
st.dataframe(event_summary, width="stretch", hide_index=True)

st.subheader("Sensor response summary")
response_summary = pd.read_csv(generated["sensor_response_summary_csv"])
st.dataframe(response_summary, width="stretch", hide_index=True)

st.subheader("Synthetic dashboard map")
map_html = Path(generated["synthetic_map_html"]).read_text(encoding="utf-8")
map_data_uri = "data:text/html;base64," + base64.b64encode(map_html.encode("utf-8")).decode("ascii")
st.iframe(map_data_uri, height=650, width="stretch")

st.subheader("Download generated outputs")

download_cols = st.columns(4)

with download_cols[0]:
    st.download_button(
        "Event summary CSV",
        data=Path(generated["event_summary_csv"]).read_bytes(),
        file_name="event_summary.csv",
        mime="text/csv",
    )

with download_cols[1]:
    st.download_button(
        "Status summary CSV",
        data=Path(generated["status_summary_csv"]).read_bytes(),
        file_name="status_summary.csv",
        mime="text/csv",
    )

with download_cols[2]:
    st.download_button(
        "Response summary CSV",
        data=Path(generated["sensor_response_summary_csv"]).read_bytes(),
        file_name="sensor_response_summary.csv",
        mime="text/csv",
    )

with download_cols[3]:
    st.download_button(
        "HTML report",
        data=Path(generated["report_html"]).read_bytes(),
        file_name="synthetic_network_report.html",
        mime="text/html",
    )

st.markdown("---")
st.markdown(
    """
### Interpretation

This app demonstrates the public workflow only. It validates that the synthetic pipeline can run end to end:
synthetic telemetry generation, rainfall-event detection, response summaries, status checks, plotting, reporting,
and dashboard-style map rendering.

It does **not** validate real operational telemetry, real hydraulic performance, production anomaly detection,
or site-specific monitoring thresholds.
"""
)
