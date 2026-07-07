"""Fix final README Markdown formatting issues.

Run from the repository root:

    python scripts/fix_readme_markdown_formatting.py

This fixes:
1. A missing closing code fence after `urban-drainage-qaqc network-demo`
   in the command-line usage section.
2. A duplicated source-tree comment on `synthetic_network.py`.
3. The validation block so it also mentions the network demo.
"""

from pathlib import Path

README = Path("README.md")


def main() -> None:
    text = README.read_text(encoding="utf-8")

    broken_network_block = """Run the synthetic network demo:

```bash
urban-drainage-qaqc network-demo

Keep private audit outputs outside Git or in ignored folders.
"""

    fixed_network_block = """Run the synthetic network demo:

```bash
urban-drainage-qaqc network-demo
```

Keep private audit outputs outside Git or in ignored folders.
"""

    text = text.replace(broken_network_block, fixed_network_block)

    text = text.replace(
        "├── synthetic_network.py # synthetic multi-sensor network generation      # synthetic telemetry generation",
        "├── synthetic_network.py # synthetic multi-sensor network generation",
    )

    # Optional polish: include the network demo in the validation section if it is missing.
    text = text.replace(
        "urban-drainage-qaqc map-demo\nruff check .",
        "urban-drainage-qaqc map-demo\nurban-drainage-qaqc network-demo\nruff check .",
    )
    text = text.replace(
        "synthetic map generated\nruff passes",
        "synthetic map generated\nsynthetic network demo generated\nruff passes",
    )

    README.write_text(text, encoding="utf-8")
    print("Fixed README Markdown formatting.")


if __name__ == "__main__":
    main()
