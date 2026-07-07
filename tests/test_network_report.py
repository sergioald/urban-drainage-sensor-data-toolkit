from urban_drainage_sensor_toolkit.network_report import run_synthetic_network_demo


def test_run_synthetic_network_demo_writes_outputs(tmp_path):
    generated = run_synthetic_network_demo(tmp_path, periods=96)

    expected = [
        "report_html",
        "network_summary_csv",
        "event_summary_csv",
        "sensor_response_summary_csv",
        "status_summary_csv",
        "rainfall_level_flow_plot",
        "synthetic_map_html",
    ]

    for key in expected:
        assert generated[key].exists()

    html = generated["report_html"].read_text(encoding="utf-8")
    assert "Synthetic urban drainage network demo" in html
    assert "Rainfall event summary" in html
