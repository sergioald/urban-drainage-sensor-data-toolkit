from pathlib import Path

from urban_drainage_sensor_toolkit.cli import main


def test_cli_demo_creates_report(tmp_path: Path):
    exit_code = main(["demo", "--output", str(tmp_path / "demo")])
    assert exit_code == 0
    assert (tmp_path / "demo" / "report" / "report.html").exists()
    assert (tmp_path / "demo" / "report" / "summary.csv").exists()


def test_cli_audit_handles_mixed_nested_private_style_folder(tmp_path: Path):
    data = tmp_path / "DATA"
    telemetry = data / "DATA_POST_PP"
    mapping = data / "DATA_PLV_VICINO"
    telemetry.mkdir(parents=True)
    mapping.mkdir(parents=True)

    (telemetry / "sample.csv").write_text(
        "DATAORA;TENSIONE BATTERIA;DOPPLER - PORTATA\n"
        "2020-09-14 07:00:00;12,1;1,2\n"
        "2020-09-14 07:06:00;12,1;1,3\n",
        encoding="utf-8",
    )
    (mapping / "nearest.csv").write_text(
        "NOME;PLV_DST_Km\nSensor_A;0,4\n",
        encoding="utf-8",
    )

    out = tmp_path / "audit"
    exit_code = main(["audit", "--input", str(data), "--output", str(out)])
    assert exit_code == 0
    assert (out / "private_data_audit.csv").exists()
    assert (out / "folder_summary.csv").exists()
    assert (out / "private_data_audit.md").exists()


def test_cli_run_skips_non_timeseries_tables(tmp_path: Path):
    data = tmp_path / "DATA"
    telemetry = data / "DATA_POST_PP"
    mapping = data / "DATA_PLV_VICINO"
    telemetry.mkdir(parents=True)
    mapping.mkdir(parents=True)

    (telemetry / "sample.csv").write_text(
        "DATAORA;TENSIONE BATTERIA;DOPPLER - PORTATA\n"
        "2020-09-14 07:00:00;12,1;1,2\n"
        "2020-09-14 07:06:00;12,1;1,3\n",
        encoding="utf-8",
    )
    (mapping / "nearest.csv").write_text("NOME;PLV_DST_Km\nSensor_A;0,4\n", encoding="utf-8")

    out = tmp_path / "report"
    exit_code = main(
        ["run", "--input", str(data), "--output", str(out), "--skip-cleaned-files"]
    )
    assert exit_code == 0
    assert (out / "report.html").exists()
    assert (out / "file_inventory.csv").exists()
    assert (out / "summary.csv").exists()


def test_cli_audit_detects_private_input_wide_rainfall_matrix(tmp_path: Path):
    input_root = tmp_path / "INPUT"
    pluvio = input_root / "PLUVIO"
    pluvio.mkdir(parents=True)

    (pluvio / "PP_ORARIA.csv").write_text(
        "CLIENTE,COMMESSA,ID_PDM,LAT,LON,2020-09-07_00,2020-09-07_01\n"
        "Client_A,Project_A,P001,0,0,1.0,2.0\n",
        encoding="utf-8",
    )
    (input_root / "INPUT_CONFIGURAZIONE.csv").write_text(
        "CLIENTE;COMMESSA;ID_PDM;FILE_Path;SIM\n"
        "Client_A;Project_A;P001;private/path;000\n",
        encoding="utf-8",
    )

    out = tmp_path / "audit"
    exit_code = main(["audit", "--input", str(input_root), "--output", str(out)])
    assert exit_code == 0

    text = (out / "private_data_audit.md").read_text(encoding="utf-8")
    assert "rainfall_wide_hourly_matrix" in text
    assert "wide hourly matrix" in text
    assert (out / "all_file_inventory.csv").exists()
