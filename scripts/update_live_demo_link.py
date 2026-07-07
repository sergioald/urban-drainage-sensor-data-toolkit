"""Update README and live-demo documentation with the deployed Streamlit URL.

Run from the repository root:

    python scripts/update_live_demo_link.py
"""

from __future__ import annotations

from pathlib import Path

STREAMLIT_URL = "https://urban-drainage-sensor-data-toolkit.streamlit.app/"

README = Path("README.md")
LIVE_DEMO_DOC = Path("docs/live_demo.md")

README_SECTION = f"""## Live demo

Try the synthetic urban drainage monitoring demo online:

[Open the live Streamlit demo]({STREAMLIT_URL})

The demo uses synthetic data only and shows rainfall-event detection, level/flow response summaries, status-rule checks, report outputs, and a synthetic dashboard map.

To run it locally:

```bash
streamlit run app.py
```

See [docs/live_demo.md](docs/live_demo.md) for scope and interpretation notes.

---
"""


def main() -> None:
    update_readme()
    update_live_demo_doc()
    print("Updated live demo link in README and docs/live_demo.md.")


def update_readme() -> None:
    if not README.exists():
        raise FileNotFoundError("README.md not found. Run this script from the repository root.")

    text = README.read_text(encoding="utf-8")

    if "## Live demo" in text:
        start = text.index("## Live demo")
        after_start = text[start:]
        separator = "\n---\n"
        if separator not in after_start:
            raise RuntimeError("Could not find the end of the existing README live-demo section.")
        end = start + after_start.index(separator) + len(separator)
        text = text[:start] + README_SECTION + text[end:]
    else:
        marker = "---\n\n## Why this repository matters"
        if marker in text:
            text = text.replace(marker, README_SECTION + "\n## Why this repository matters")
        else:
            text = README_SECTION + "\n" + text

    README.write_text(text, encoding="utf-8")


def update_live_demo_doc() -> None:
    if not LIVE_DEMO_DOC.exists():
        return

    text = LIVE_DEMO_DOC.read_text(encoding="utf-8")

    live_line = f"[Open the live Streamlit demo]({STREAMLIT_URL})"
    if live_line in text:
        return

    block = f"""## Live app

{live_line}

"""

    if "## Live app" in text:
        start = text.index("## Live app")
        next_heading = text.find("\n## ", start + 1)
        if next_heading == -1:
            text = text[:start] + block
        else:
            text = text[:start] + block + text[next_heading + 1 :]
    else:
        first_heading_end = text.find("\n\n")
        if first_heading_end == -1:
            text = text + "\n\n" + block
        else:
            text = text[: first_heading_end + 2] + block + text[first_heading_end + 2 :]

    LIVE_DEMO_DOC.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
