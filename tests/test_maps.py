from pathlib import Path

from urban_drainage_sensor_toolkit.maps import (
    create_synthetic_monitoring_points,
    render_leaflet_map,
)


def test_create_synthetic_monitoring_points_has_required_columns():
    points = create_synthetic_monitoring_points()

    required = {
        "point_id",
        "latitude",
        "longitude",
        "status",
        "data_delayed",
        "battery_warning",
        "missing_data",
    }

    assert required.issubset(points.columns)
    assert len(points) >= 10


def test_render_leaflet_map_writes_dashboard_html(tmp_path: Path):
    points = create_synthetic_monitoring_points()
    output_html = render_leaflet_map(points, tmp_path / "map.html")

    text = output_html.read_text(encoding="utf-8")

    assert output_html.exists()
    assert "Synthetic urban drainage monitoring dashboard" in text
    assert "cartodb dark matter" in text
    assert "Layers and QA/QC filters" in text
    assert "ID PDM" in text
    assert "leaflet.markercluster" in text
    assert "PDM_001" in text
    assert "CLIENTE" not in text
    assert "COMMESSA" not in text
