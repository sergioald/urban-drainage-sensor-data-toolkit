from urban_drainage_sensor_toolkit.reporting import run_folder_report
from urban_drainage_sensor_toolkit.synthetic import create_synthetic_monitoring_csv


def test_run_folder_report_writes_summary_plot(tmp_path):
    data_dir = tmp_path / "data"
    report_dir = tmp_path / "report"
    create_synthetic_monitoring_csv(data_dir / "synthetic.csv", periods=24)

    generated = run_folder_report(data_dir, report_dir)

    assert generated["report_summary_plot"].exists()
    assert (report_dir / "report_summary.png").exists()
    assert "report_summary.png" in (report_dir / "report.html").read_text(encoding="utf-8")
