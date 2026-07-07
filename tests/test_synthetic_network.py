from urban_drainage_sensor_toolkit.synthetic_network import (
    create_synthetic_network_frames,
    write_synthetic_network,
)


def test_create_synthetic_network_frames():
    frames = create_synthetic_network_frames(periods=48)

    assert {"rain_gauge_001", "level_sensor_001", "level_sensor_002", "flow_sensor_001"}.issubset(frames)
    assert len(frames["rain_gauge_001"]) == 48
    assert "rainfall_mm" in frames["rain_gauge_001"].columns
    assert "level_m" in frames["level_sensor_001"].columns
    assert "flow_lps" in frames["flow_sensor_001"].columns


def test_write_synthetic_network(tmp_path):
    paths = write_synthetic_network(tmp_path, periods=48)

    assert paths["rain_gauge_001"].exists()
    assert paths["monitoring_points"].exists()
