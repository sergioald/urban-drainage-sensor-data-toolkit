"""Public-safe synthetic map generation utilities.

This module creates small Leaflet HTML maps from synthetic or anonymised point
metadata. It does not depend on private operational data and should not be used
to publish real coordinates, client names, project names, or asset identifiers.

The dashboard-style output intentionally resembles an operational monitoring map
while keeping every point, label, filter, and coordinate synthetic.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd

_STATUS_STYLE: dict[str, dict[str, str]] = {
    "normal": {"colour": "#2ca25f", "symbol": "●", "label": "Normal"},
    "warning": {"colour": "#feb24c", "symbol": "▲", "label": "Warning"},
    "offline": {"colour": "#de2d26", "symbol": "■", "label": "Offline"},
    "maintenance": {"colour": "#756bb1", "symbol": "◆", "label": "Maintenance"},
}

_FLAG_COLUMNS = [
    "data_delayed",
    "battery_warning",
    "level_low",
    "flow_high",
    "sensor_dirty",
    "missing_data",
]

_TRUE_TOKENS = {"1", "true", "yes", "y", "si", "s", "on"}
_FALSE_TOKENS = {"0", "false", "no", "n", "none", "nan", "na", "", "off"}


def create_synthetic_monitoring_points() -> pd.DataFrame:
    """Create public-safe synthetic monitoring points.

    The coordinates, point IDs, networks, and status flags are fictional. They
    are designed to mimic the structure of an urban drainage monitoring
    dashboard without exposing operational locations.
    """

    rows = [
        ("PDM_001", "Synthetic_North", "level", "normal", 55.945, -3.205, 1.5, False, False, False, False, False, False),
        ("PDM_002", "Synthetic_North", "flow", "warning", 55.952, -3.193, 8.0, True, False, False, True, False, False),
        ("PDM_003", "Synthetic_Central", "rainfall", "normal", 55.939, -3.184, 0.5, False, False, False, False, False, False),
        ("PDM_004", "Synthetic_Central", "level", "offline", 55.934, -3.213, 48.0, True, True, False, False, False, True),
        ("PDM_005", "Synthetic_South", "flow", "normal", 55.926, -3.198, 2.25, False, False, False, False, False, False),
        ("PDM_006", "Synthetic_North", "pressure", "warning", 55.949, -3.202, 11.0, True, True, False, False, False, False),
        ("PDM_007", "Synthetic_North", "level", "normal", 55.947, -3.196, 3.0, False, False, True, False, False, False),
        ("PDM_008", "Synthetic_East", "flow", "warning", 55.943, -3.188, 6.0, False, False, False, True, True, False),
        ("PDM_009", "Synthetic_East", "level", "maintenance", 55.937, -3.181, 4.0, False, False, False, False, False, False),
        ("PDM_010", "Synthetic_South", "rainfall", "normal", 55.930, -3.191, 1.0, False, False, False, False, False, False),
        ("PDM_011", "Synthetic_West", "level", "warning", 55.940, -3.218, 9.5, True, False, True, False, False, False),
        ("PDM_012", "Synthetic_West", "flow", "offline", 55.936, -3.222, 72.0, True, True, False, False, True, True),
        ("PDM_013", "Synthetic_Central", "pressure", "normal", 55.941, -3.199, 2.0, False, False, False, False, False, False),
        ("PDM_014", "Synthetic_Central", "level", "warning", 55.942, -3.197, 5.0, False, False, True, False, False, False),
        ("PDM_015", "Synthetic_Central", "flow", "normal", 55.944, -3.200, 1.2, False, False, False, False, False, False),
        ("PDM_016", "Synthetic_East", "rainfall", "normal", 55.946, -3.186, 0.8, False, False, False, False, False, False),
        ("PDM_017", "Synthetic_South", "level", "warning", 55.928, -3.206, 7.2, True, False, False, False, True, False),
        ("PDM_018", "Synthetic_South", "flow", "normal", 55.924, -3.202, 1.6, False, False, False, False, False, False),
    ]

    columns = [
        "point_id",
        "network",
        "asset_type",
        "status",
        "latitude",
        "longitude",
        "last_contact_hours",
        "data_delayed",
        "battery_warning",
        "level_low",
        "flow_high",
        "sensor_dirty",
        "missing_data",
    ]
    return pd.DataFrame(rows, columns=columns)


def synthetic_region_boundaries() -> list[dict[str, object]]:
    """Return simple fictional region boundaries for the synthetic map."""

    return [
        {
            "name": "Synthetic North Basin",
            "coordinates": [
                [55.956, -3.224],
                [55.956, -3.190],
                [55.944, -3.176],
                [55.935, -3.194],
                [55.940, -3.222],
                [55.956, -3.224],
            ],
        },
        {
            "name": "Synthetic South Basin",
            "coordinates": [
                [55.939, -3.224],
                [55.934, -3.194],
                [55.922, -3.184],
                [55.919, -3.212],
                [55.929, -3.229],
                [55.939, -3.224],
            ],
        },
    ]


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


def _status_style(status: object) -> dict[str, str]:
    status_key = str(status).strip().lower()
    return _STATUS_STYLE.get(
        status_key,
        {"colour": "#4ea3f1", "symbol": "●", "label": str(status)},
    )


def _coerce_bool(value: object) -> bool:
    """Convert common CSV boolean encodings without treating 'False' as True."""

    if isinstance(value, bool):
        return value
    if value is None or pd.isna(value):
        return False

    token = str(value).strip().lower()
    if token in _TRUE_TOKENS:
        return True
    if token in _FALSE_TOKENS:
        return False
    return False


def _serialise_points(
    points: pd.DataFrame,
    *,
    latitude_col: str,
    longitude_col: str,
    point_id_col: str,
    status_col: str,
) -> list[dict[str, object]]:
    marker_payload = []
    for _, row in points.iterrows():
        point_id = str(row.get(point_id_col, "Point"))
        status = str(row.get(status_col, "unknown"))
        style = _status_style(status)

        flags = {
            col: _coerce_bool(row.get(col, False))
            for col in _FLAG_COLUMNS
            if col in points.columns
        }

        popup_rows = []
        for col in points.columns:
            if col in {latitude_col, longitude_col}:
                continue
            value = html.escape(str(row.get(col, "")))
            popup_rows.append(f"<b>{html.escape(str(col))}</b>: {value}")

        marker_payload.append(
            {
                "lat": float(row[latitude_col]),
                "lon": float(row[longitude_col]),
                "point_id": html.escape(point_id),
                "search_id": point_id.lower(),
                "status": html.escape(status),
                "network": html.escape(str(row.get("network", ""))),
                "asset_type": html.escape(str(row.get("asset_type", ""))),
                "colour": style["colour"],
                "symbol": style["symbol"],
                "popup": "<br>".join(popup_rows),
                "flags": flags,
            }
        )
    return marker_payload


def render_leaflet_map(
    points: pd.DataFrame,
    output_html: str | Path,
    *,
    latitude_col: str = "latitude",
    longitude_col: str = "longitude",
    point_id_col: str = "point_id",
    status_col: str = "status",
    title: str = "Synthetic urban drainage monitoring dashboard",
) -> Path:
    """Render a public-safe synthetic Leaflet monitoring dashboard.

    The output includes a dark basemap, clustered synthetic markers, fictional
    region boundaries, a search box, status filters, and QA/QC flag filters. The
    controls are intended to reflect the structure of an operational monitoring
    workflow without exposing private information.

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

    marker_json = json.dumps(
        _serialise_points(
            work,
            latitude_col=latitude_col,
            longitude_col=longitude_col,
            point_id_col=point_id_col,
            status_col=status_col,
        ),
        ensure_ascii=False,
    )
    boundary_json = json.dumps(synthetic_region_boundaries(), ensure_ascii=False)
    safe_title = html.escape(title)

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
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"
  />
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"
  />
  <style>
    html, body, #map {{
      height: 100%;
      width: 100%;
      margin: 0;
      font-family: Arial, sans-serif;
      background: #111;
    }}
    .banner {{
      position: absolute;
      top: 12px;
      left: 52px;
      z-index: 1000;
      background: rgba(17, 17, 17, 0.88);
      color: #f5f5f5;
      padding: 10px 12px;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      max-width: 390px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
    }}
    .banner h1 {{
      font-size: 16px;
      line-height: 1.2;
      margin: 0 0 4px 0;
    }}
    .banner p {{
      font-size: 12px;
      line-height: 1.35;
      margin: 0;
      color: #d7d7d7;
    }}
    .search-panel {{
      position: absolute;
      top: 106px;
      left: 12px;
      z-index: 1000;
      display: flex;
      background: rgba(255, 255, 255, 0.94);
      border-radius: 4px;
      overflow: hidden;
      border: 1px solid #aaa;
    }}
    .search-panel input {{
      width: 135px;
      padding: 7px;
      border: 0;
      outline: 0;
      font-size: 12px;
    }}
    .search-panel button {{
      width: 38px;
      border: 0;
      background: #f2f2f2;
      cursor: pointer;
      font-size: 16px;
    }}
    .control-panel {{
      position: absolute;
      right: 14px;
      top: 76px;
      bottom: 30px;
      z-index: 1000;
      width: 225px;
      background: rgba(255, 255, 255, 0.94);
      color: #222;
      padding: 10px 12px;
      border-radius: 6px;
      overflow-y: auto;
      border: 1px solid #aaa;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.45);
      font-size: 12px;
    }}
    .control-panel h2 {{
      font-size: 15px;
      margin: 4px 0 8px 0;
    }}
    .control-panel h3 {{
      font-size: 13px;
      margin: 12px 0 6px 0;
      border-bottom: 1px solid #ddd;
      padding-bottom: 3px;
    }}
    .control-panel label {{
      display: block;
      margin: 5px 0;
      white-space: nowrap;
    }}
    .mock-marker {{
      width: 28px;
      height: 28px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      border: 2px solid rgba(255, 255, 255, 0.88);
      box-shadow: 0 1px 6px rgba(0,0,0,0.55);
      text-align: center;
    }}
    .mock-marker span {{
      display: block;
      transform: rotate(45deg);
      color: white;
      font-weight: bold;
      font-size: 15px;
      line-height: 26px;
    }}
    .legend {{
      background: rgba(255, 255, 255, 0.94);
      padding: 0.6rem 0.8rem;
      border: 1px solid #aaa;
      border-radius: 0.4rem;
      line-height: 1.5;
      color: #222;
      font-size: 12px;
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
  <div id="map"></div>

  <div class="banner">
    <h1>{safe_title}</h1>
    <p>
      Public-safe mock-up using synthetic points, fictional IDs and synthetic
      QA/QC flags. No real coordinates or operational identifiers are included.
    </p>
  </div>

  <div class="search-panel">
    <input id="pointSearch" placeholder="ID PDM" aria-label="Search synthetic point ID">
    <button onclick="applyFilters()" title="Search">⌕</button>
  </div>

  <div class="control-panel">
    <h2>Layers and QA/QC filters</h2>
    <h3>Base map</h3>
    <label><input type="radio" name="basemap" value="dark" checked> cartodb dark matter</label>
    <label><input type="radio" name="basemap" value="osm"> openstreetmap</label>

    <h3>Overlay</h3>
    <label><input type="checkbox" id="regionsLayer" checked> Synthetic regions</label>
    <label><input type="checkbox" id="clusterLayer" checked> Cluster points</label>

    <h3>Status</h3>
    <label><input type="checkbox" class="status-filter" value="normal" checked> Normal</label>
    <label><input type="checkbox" class="status-filter" value="warning" checked> Warning</label>
    <label><input type="checkbox" class="status-filter" value="offline" checked> Offline</label>
    <label><input type="checkbox" class="status-filter" value="maintenance" checked> Maintenance</label>

    <h3>QA/QC flags</h3>
    <label><input type="checkbox" class="flag-filter" value="data_delayed"> Data delayed</label>
    <label><input type="checkbox" class="flag-filter" value="battery_warning"> Battery warning</label>
    <label><input type="checkbox" class="flag-filter" value="level_low"> Low level</label>
    <label><input type="checkbox" class="flag-filter" value="flow_high"> High flow</label>
    <label><input type="checkbox" class="flag-filter" value="sensor_dirty"> Dirty sensor</label>
    <label><input type="checkbox" class="flag-filter" value="missing_data"> Missing data</label>
  </div>

  <script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin="">
  </script>
  <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
  <script>
    const markers = {marker_json};
    const regions = {boundary_json};
    const map = L.map("map").setView([{center_lat:.6f}, {center_lon:.6f}], 13);

    const darkLayer = L.tileLayer(
      "https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png",
      {{
        attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
        subdomains: "abcd",
        maxZoom: 20
      }}
    );

    const osmLayer = L.tileLayer(
      "https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",
      {{
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
      }}
    );

    darkLayer.addTo(map);

    const regionGroup = L.layerGroup().addTo(map);
    const pointGroup = L.markerClusterGroup({{ disableClusteringAtZoom: 15 }}).addTo(map);
    const unclusteredGroup = L.layerGroup();

    function markerIcon(item) {{
      return L.divIcon({{
        className: "",
        html: `<div class="mock-marker" style="background:${{item.colour}}"><span>${{item.symbol}}</span></div>`,
        iconSize: [30, 42],
        iconAnchor: [15, 42],
        popupAnchor: [0, -36]
      }});
    }}

    function drawRegions() {{
      regionGroup.clearLayers();
      if (!document.getElementById("regionsLayer").checked) {{
        return;
      }}
      regions.forEach((region) => {{
        const polygon = L.polygon(region.coordinates, {{
          color: "#16a516",
          weight: 2,
          opacity: 0.85,
          fillOpacity: 0.05
        }}).addTo(regionGroup);
        polygon.bindTooltip(region.name);
      }});
    }}

    function selectedStatuses() {{
      return Array.from(document.querySelectorAll(".status-filter:checked"))
        .map((item) => item.value);
    }}

    function selectedFlags() {{
      return Array.from(document.querySelectorAll(".flag-filter:checked"))
        .map((item) => item.value);
    }}

    function markerMatches(item) {{
      const query = document.getElementById("pointSearch").value.trim().toLowerCase();
      const statusSet = selectedStatuses();
      const flags = selectedFlags();

      if (query && !item.search_id.includes(query)) {{
        return false;
      }}
      if (!statusSet.includes(item.status.toLowerCase())) {{
        return false;
      }}
      return flags.every((flag) => item.flags[flag] === true);
    }}

    function addMarkerToGroup(item, group) {{
      const marker = L.marker([item.lat, item.lon], {{ icon: markerIcon(item) }});
      marker.bindPopup(item.popup);
      marker.bindTooltip(item.point_id);
      group.addLayer(marker);
    }}

    function drawMarkers() {{
      pointGroup.clearLayers();
      unclusteredGroup.clearLayers();
      const useCluster = document.getElementById("clusterLayer").checked;

      markers.filter(markerMatches).forEach((item) => {{
        addMarkerToGroup(item, useCluster ? pointGroup : unclusteredGroup);
      }});

      if (useCluster) {{
        if (!map.hasLayer(pointGroup)) {{
          map.addLayer(pointGroup);
        }}
        if (map.hasLayer(unclusteredGroup)) {{
          map.removeLayer(unclusteredGroup);
        }}
      }} else {{
        if (!map.hasLayer(unclusteredGroup)) {{
          map.addLayer(unclusteredGroup);
        }}
        if (map.hasLayer(pointGroup)) {{
          map.removeLayer(pointGroup);
        }}
      }}
    }}

    function applyFilters() {{
      drawRegions();
      drawMarkers();
    }}

    document.querySelectorAll("input").forEach((item) => {{
      item.addEventListener("change", applyFilters);
      item.addEventListener("keyup", applyFilters);
    }});

    document.querySelectorAll("input[name='basemap']").forEach((item) => {{
      item.addEventListener("change", () => {{
        if (item.value === "dark" && item.checked) {{
          map.removeLayer(osmLayer);
          darkLayer.addTo(map);
        }}
        if (item.value === "osm" && item.checked) {{
          map.removeLayer(darkLayer);
          osmLayer.addTo(map);
        }}
      }});
    }});

    const legend = L.control({{position: "bottomright"}});
    legend.onAdd = function () {{
      const div = L.DomUtil.create("div", "legend");
      div.innerHTML = `
        <b>Synthetic status</b><br>
        <span class="swatch" style="background:#2ca25f"></span>normal<br>
        <span class="swatch" style="background:#feb24c"></span>warning<br>
        <span class="swatch" style="background:#de2d26"></span>offline<br>
        <span class="swatch" style="background:#756bb1"></span>maintenance
      `;
      return div;
    }};
    legend.addTo(map);

    drawRegions();
    drawMarkers();
  </script>
</body>
</html>
"""

    output_path.write_text(document, encoding="utf-8")
    return output_path
