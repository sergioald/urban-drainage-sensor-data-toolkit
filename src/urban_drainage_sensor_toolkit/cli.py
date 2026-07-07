from __future__ import annotations

import argparse
from pathlib import Path

from .audit import write_audit_report
from .maps import create_synthetic_monitoring_points, render_leaflet_map
from .network_report import run_synthetic_network_demo
from .reporting import run_folder_report
from .synthetic import create_synthetic_monitoring_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urban-drainage-qaqc",
        description="Public-safe urban drainage telemetry CSV QA/QC workflow.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Create synthetic data and run the example report")
    demo.add_argument("--output", default="examples/outputs/demo", help="Output folder")

    run = sub.add_parser("run", help="Run QA/QC over a folder of CSV files")
    run.add_argument("--input", required=True, help="Input folder containing CSV files")
    run.add_argument("--output", required=True, help="Output folder for report files")
    run.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only process CSV files directly inside the input folder",
    )
    run.add_argument(
        "--skip-cleaned-files",
        action="store_true",
        help="Do not write potentially large *_cleaned.csv outputs",
    )

    audit = sub.add_parser(
        "audit",
        help="Audit a private data folder and write schema/timing reports without row values",
    )
    audit.add_argument("--input", required=True, help="Private DATA folder to inspect")
    audit.add_argument("--output", required=True, help="Output folder for audit reports")
    audit.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only inspect CSV files directly inside the input folder",
    )

    synth = sub.add_parser("create-synthetic", help="Create one synthetic monitoring CSV")
    synth.add_argument("--output", default="examples/data/synthetic_monitoring_point.csv")
    synth.add_argument("--periods", type=int, default=192)

    map_demo = sub.add_parser(
        "map-demo",
        help="Create a public-safe synthetic monitoring dashboard map",
    )
    map_demo.add_argument(
        "--output",
        default="examples/outputs/synthetic_map",
        help="Output folder for synthetic map files",
    )

    network_demo = sub.add_parser(
        "network-demo",
        help="Run the synthetic multi-sensor urban drainage network demo",
    )
    network_demo.add_argument(
        "--output",
        default="examples/outputs/network_demo",
        help="Output folder for the synthetic network demo",
    )
    network_demo.add_argument(
        "--periods",
        type=int,
        default=336,
        help="Number of synthetic records per telemetry series",
    )

    return parser


def _run_map_demo(output_folder: str | Path) -> dict[str, Path]:
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    points = create_synthetic_monitoring_points()
    csv_path = output_dir / "synthetic_monitoring_points.csv"
    html_path = output_dir / "synthetic_monitoring_points.html"

    points.to_csv(csv_path, index=False)
    render_leaflet_map(
        points,
        html_path,
        title="Synthetic urban drainage monitoring dashboard",
    )

    return {"csv": csv_path, "html": html_path}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "create-synthetic":
        path = create_synthetic_monitoring_csv(args.output, periods=args.periods)
        print(f"Created {path}")
        return 0

    if args.command == "demo":
        output = Path(args.output)
        data_dir = output / "data"
        create_synthetic_monitoring_csv(data_dir / "synthetic_monitoring_point.csv")
        generated = run_folder_report(data_dir, output / "report")
        print(f"Report written to {generated['html_report']}")
        return 0

    if args.command == "map-demo":
        generated = _run_map_demo(args.output)
        print(f"Synthetic point table written to {generated['csv']}")
        print(f"Synthetic dashboard map written to {generated['html']}")
        return 0

    if args.command == "network-demo":
        generated = run_synthetic_network_demo(args.output, periods=args.periods)
        print(f"Network report written to {generated['report_html']}")
        print(f"Synthetic dashboard map written to {generated['synthetic_map_html']}")
        return 0

    if args.command == "audit":
        generated = write_audit_report(
            args.input,
            args.output,
            recursive=not args.non_recursive,
        )
        print(f"Audit written to {generated['markdown_report']}")
        return 0

    if args.command == "run":
        generated = run_folder_report(
            args.input,
            args.output,
            recursive=not args.non_recursive,
            write_cleaned=not args.skip_cleaned_files,
        )
        print(f"Report written to {generated['html_report']}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
