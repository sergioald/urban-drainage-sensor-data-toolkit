"""Create a small private sample ZIP for validation outside the public repository.

This utility intentionally avoids copying files from a previous output folder if
that folder lives under the data root. Review the generated files manually before
sharing them with anyone.
"""

from __future__ import annotations

import argparse
import csv
import random
import shutil
import zipfile
from collections import Counter
from pathlib import Path

EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    "PRIVATE_SAMPLE_FOR_CHAT",
    "PRIVATE_SAMPLE_FOR_VALIDATION",
}


def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def _is_excluded(path: Path, output_dir: Path) -> bool:
    path = path.resolve()
    output_dir = output_dir.resolve()
    if path == output_dir or output_dir in path.parents:
        return True
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def iter_candidate_files(root: Path, folder: Path, output_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file() and not _is_excluded(path, output_dir)
    )


def scan_data_folder(root: Path, output_dir: Path) -> list[dict[str, object]]:
    rows = []
    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        if folder.name in EXCLUDED_DIR_NAMES or folder == output_dir:
            continue
        files = iter_candidate_files(root, folder, output_dir)
        ext_counts = Counter(path.suffix.lower() or "[no extension]" for path in files)
        total_size = sum(path.stat().st_size for path in files)
        rows.append(
            {
                "folder": folder.name,
                "file_count": len(files),
                "total_size_bytes": total_size,
                "total_size_readable": human_size(total_size),
                "extensions": "; ".join(
                    f"{ext}: {count}" for ext, count in sorted(ext_counts.items())
                ),
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]], output_csv: Path) -> None:
    if not rows:
        return
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def copy_random_samples(root: Path, output_dir: Path, n_per_folder: int, seed: int) -> Path:
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []

    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        if folder.name in EXCLUDED_DIR_NAMES or folder == output_dir:
            continue
        files = iter_candidate_files(root, folder, output_dir)
        selected = rng.sample(files, min(n_per_folder, len(files))) if files else []
        target_folder = output_dir / folder.name
        target_folder.mkdir(parents=True, exist_ok=True)

        for index, source in enumerate(selected, start=1):
            destination = target_folder / f"sample_{index:03d}{source.suffix.lower()}"
            shutil.copy2(source, destination)
            manifest_rows.append(
                {
                    "original_folder": folder.name,
                    "original_relative_path": str(source.relative_to(root)),
                    "sample_file": str(destination.relative_to(output_dir)),
                    "size": human_size(source.stat().st_size),
                }
            )

    manifest_csv = output_dir / "sample_manifest_private_check_before_uploading.csv"
    write_csv(manifest_rows, manifest_csv)
    return manifest_csv


def zip_folder(folder: Path, zip_path: Path) -> Path:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(folder.parent))
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Path to the private DATA folder")
    parser.add_argument("--n", type=int, default=3, help="Files to copy per top-level folder")
    parser.add_argument(
        "--output",
        default="PRIVATE_SAMPLE_FOR_VALIDATION",
        help="Output folder name, created inside the DATA folder unless absolute",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--zip", action="store_true", help="Also create a ZIP next to the output folder")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)

    output_dir = Path(args.output).expanduser()
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir = output_dir.resolve()

    inventory = scan_data_folder(root, output_dir)
    inventory_csv = root / "data_folder_inventory.csv"
    write_csv(inventory, inventory_csv)
    print(f"Inventory written to: {inventory_csv}")

    manifest = copy_random_samples(root, output_dir, args.n, args.seed)
    print(f"Sample manifest written to: {manifest}")
    print("Review the copied files manually before uploading or sharing them.")

    if args.zip:
        zip_path = output_dir.with_suffix(".zip")
        zip_folder(output_dir, zip_path)
        print(f"ZIP written to: {zip_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
