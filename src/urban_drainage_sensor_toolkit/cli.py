from __future__ import annotations

import argparse
from pathlib import Path

from .audit import write_audit_report
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

    return parser


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
