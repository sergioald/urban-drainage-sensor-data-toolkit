from pathlib import Path

from urban_drainage_sensor_toolkit.maps import (
    create_synthetic_monitoring_points,
    render_leaflet_map,
)


def test_create_synthetic_monitoring_points_has_required_columns():
    points = create_synthetic_monitoring_points()

    assert {"point_id", "latitude", "longitude", "status"}.issubset(points.columns)
    assert len(points) >= 3


def test_render_leaflet_map_writes_html(tmp_path: Path):
    points = create_synthetic_monitoring_points()
    output_html = render_leaflet_map(points, tmp_path / "map.html")

    text = output_html.read_text(encoding="utf-8")

    assert output_html.exists()
    assert "Synthetic monitoring-point map" in text
    assert "Leaflet" in text or "leaflet" in text
    assert "Point_001" in text
    assert "CLIENTE" not in text
    assert "COMMESSA" not in text
    assert "ID PDM" not in text
