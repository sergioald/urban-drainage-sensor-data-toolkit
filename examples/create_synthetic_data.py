from pathlib import Path

from urban_drainage_sensor_toolkit.synthetic import create_synthetic_monitoring_csv

if __name__ == "__main__":
    path = create_synthetic_monitoring_csv(Path(__file__).parent / "data" / "synthetic_monitoring_point.csv")
    print(f"Created {path}")
