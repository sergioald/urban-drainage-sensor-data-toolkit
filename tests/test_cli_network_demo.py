from urban_drainage_sensor_toolkit.cli import main


def test_network_demo_cli_writes_outputs(tmp_path):
    code = main(["network-demo", "--output", str(tmp_path), "--periods", "96"])

    assert code == 0
    assert (tmp_path / "report.html").exists()
    assert (tmp_path / "event_summary.csv").exists()
    assert (tmp_path / "synthetic_monitoring_points.html").exists()
