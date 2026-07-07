from urban_drainage_sensor_toolkit.cli import main


def test_map_demo_cli_writes_outputs(tmp_path):
    code = main(["map-demo", "--output", str(tmp_path)])

    assert code == 0
    assert (tmp_path / "synthetic_monitoring_points.csv").exists()
    assert (tmp_path / "synthetic_monitoring_points.html").exists()
