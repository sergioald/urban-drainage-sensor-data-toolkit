"""Public-safe synthetic map generation utilities.

This module creates small Leaflet HTML maps from synthetic or anonymised point
metadata. It does not depend on private operational data and should not be used
to publish real coordinates or client/site identifiers.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd


def create_synthetic_monitoring_points() -> pd.DataFrame:
    """Create a small public-safe set of synthetic monitoring points.

    The coordinates are deliberately generic and should be treated as fictional
    demonstration locations.
    """

    return pd.DataFrame(
        [
            {
                "point_id": "Point_001",
                "network": "Synthetic_North",
                "asset_type": "level",
                "status": "normal",
                "latitude": 55.945,
                "longitude": -3.205,
                "last_contact_hours": 1.5,
            },
            {
                "point_id": "Point_002",
                "network": "Synthetic_North",
                "asset_type": "flow",
                "status": "warning",
                "latitude": 55.952,
                "longitude": -3.193,
                "last_contact_hours": 8.0,
            },
            {
                "point_id": "Point_003",
                "network": "Synthetic_Central",
                "asset_type": "rainfall",
                "status": "normal",
                "latitude": 55.939,
                "longitude": -3.184,
                "last_contact_hours": 0.5,
            },
            {
                "point_id": "Point_004",
                "network": "Synthetic_Central",
                "asset_type": "level",
                "status": "offline",
                "latitude": 55.934,
                "longitude": -3.213,
                "last_contact_hours": 48.0,
            },
            {
                "point_id": "Point_005",
                "network": "Synthetic_South",
                "asset_type": "flow",
                "status": "normal",
                "latitude": 55.926,
                "longitude": -3.198,
                "last_contact_hours": 2.25,
            },
        ]
    )


def _status_colour(status: str) -> str:
    """Return a simple marker colour for a synthetic point status."""

    status_key = str(status).strip().lower()
    if status_key in {"normal", "ok", "healthy"}:
        return "#2ca25f"
    if status_key in {"warning", "late", "degraded"}:
        return "#feb24c"
    if status_key in {"offline", "critical", "missing"}:
        return "#de2d26"
    return "#756bb1"


def _validate_columns(
    points: pd.DataFrame,
    *,
    latitude_col: str,
    longitude_col: str,
    point_id_col: str,
) -> None:
    required = {latitude_col, longitude_col, point_id_col}
    missing = sorted(required.difference(points.columns))
    if missing:
        raise ValueError(f"Missing required map columns: {missing}")


def render_leaflet_map(
    points: pd.DataFrame,
    output_html: str | Path,
    *,
    latitude_col: str = "latitude",
    longitude_col: str = "longitude",
    point_id_col: str = "point_id",
    status_col: str = "status",
    title: str = "Synthetic monitoring-point map",
) -> Path:
    """Render a small public-safe Leaflet map.

    Parameters
    ----------
    points:
        Table containing point metadata and synthetic/anonymised coordinates.
    output_html:
        Path where the HTML file will be written.
    latitude_col, longitude_col, point_id_col, status_col:
        Column names used to build map markers.
    title:
        HTML title and page heading.

    Returns
    -------
    pathlib.Path
        Path to the written HTML file.

    Notes
    -----
    Do not pass real private coordinates or client identifiers to this function
    for public release. Use synthetic or anonymised data only.
    """

    _validate_columns(
        points,
        latitude_col=latitude_col,
        longitude_col=longitude_col,
        point_id_col=point_id_col,
    )

    work = points.copy()
    work[latitude_col] = pd.to_numeric(work[latitude_col], errors="coerce")
    work[longitude_col] = pd.to_numeric(work[longitude_col], errors="coerce")
    work = work.dropna(subset=[latitude_col, longitude_col]).reset_index(drop=True)

    output_path = Path(output_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if work.empty:
        center_lat, center_lon = 0.0, 0.0
    else:
        center_lat = float(work[latitude_col].mean())
        center_lon = float(work[longitude_col].mean())

    marker_payload = []
    for _, row in work.iterrows():
        point_id = html.escape(str(row.get(point_id_col, "Point")))
        status = html.escape(str(row.get(status_col, "unknown")))
        colour = _status_colour(status)

        popup_rows = []
        for col in work.columns:
            if col in {latitude_col, longitude_col}:
                continue
            value = html.escape(str(row.get(col, "")))
            popup_rows.append(f"<b>{html.escape(str(col))}</b>: {value}")

        marker_payload.append(
            {
                "lat": float(row[latitude_col]),
                "lon": float(row[longitude_col]),
                "point_id": point_id,
                "status": status,
                "colour": colour,
                "popup": "<br>".join(popup_rows),
            }
        )

    safe_title = html.escape(title)
    marker_json = json.dumps(marker_payload, ensure_ascii=False)

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{safe_title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIINfQqK0xXt0N4xIiX9sJp9lH8VjY1e1vI="
    crossorigin=""
  />
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      color: #222;
    }}
    header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid #ddd;
    }}
    #map {{
      height: 76vh;
      width: 100%;
    }}
    .note {{
      font-size: 0.9rem;
      color: #555;
      margin-top: 0.25rem;
    }}
    .legend {{
      background: white;
      padding: 0.6rem 0.8rem;
      border: 1px solid #bbb;
      border-radius: 0.4rem;
      line-height: 1.5;
    }}
    .swatch {{
      display: inline-block;
      width: 0.8rem;
      height: 0.8rem;
      margin-right: 0.35rem;
      border-radius: 50%;
      vertical-align: middle;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{safe_title}</h1>
    <div class="note">
      Public-safe synthetic map. Do not replace with real private coordinates
      or client identifiers in a public repository.
    </div>
  </header>
  <div id="map"></div>

  <script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin="">
  </script>
  <script>
    const markers = {marker_json};

    const map = L.map("map").setView([{center_lat:.6f}, {center_lon:.6f}], 13);

    L.tileLayer("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors"
    }}).addTo(map);

    markers.forEach((item) => {{
      const marker = L.circleMarker([item.lat, item.lon], {{
        radius: 8,
        color: item.colour,
        fillColor: item.colour,
        fillOpacity: 0.85,
        weight: 2
      }}).addTo(map);

      marker.bindPopup(item.popup);
      marker.bindTooltip(item.point_id);
    }});

    const legend = L.control({{position: "bottomright"}});
    legend.onAdd = function () {{
      const div = L.DomUtil.create("div", "legend");
      div.innerHTML = `
        <b>Status</b><br>
        <span class="swatch" style="background:#2ca25f"></span>normal<br>
        <span class="swatch" style="background:#feb24c"></span>warning<br>
        <span class="swatch" style="background:#de2d26"></span>offline
      `;
      return div;
    }};
    legend.addTo(map);
  </script>
</body>
</html>
"""

    output_path.write_text(document, encoding="utf-8")
    return output_path
