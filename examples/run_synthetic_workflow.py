from pathlib import Path

from urban_drainage_sensor_toolkit.reporting import run_folder_report
from urban_drainage_sensor_toolkit.synthetic import create_synthetic_monitoring_csv

if __name__ == "__main__":
    base = Path(__file__).parent
    data_dir = base / "data"
    out_dir = base / "outputs" / "synthetic_report"
    create_synthetic_monitoring_csv(data_dir / "synthetic_monitoring_point.csv")
    generated = run_folder_report(data_dir, out_dir)
    print(f"Report written to {generated['html_report']}")
