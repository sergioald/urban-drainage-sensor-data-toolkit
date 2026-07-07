"""Add Streamlit live-demo metadata to README and requirements.

Run from the repository root:

    python scripts/add_streamlit_demo_metadata.py
"""

from pathlib import Path

README = Path("README.md")
REQUIREMENTS = Path("requirements.txt")
PYPROJECT = Path("pyproject.toml")

README_SECTION = """## Live demo

A browser-based synthetic demo can be deployed from `app.py` using Streamlit Community Cloud.

The demo runs the public-safe synthetic network workflow: rainfall-event detection, level/flow response summaries, status-rule checks, report outputs, and a synthetic dashboard map.

```bash
streamlit run app.py
```

See [docs/live_demo.md](docs/live_demo.md) for scope and interpretation notes.

---
"""


def main() -> None:
    _ensure_streamlit_requirement()
    _ensure_pyproject_dependency()
    _update_readme()
    print("Added Streamlit demo metadata.")


def _ensure_streamlit_requirement() -> None:
    if not REQUIREMENTS.exists():
        REQUIREMENTS.write_text("streamlit>=1.40\n", encoding="utf-8")
        return

    text = REQUIREMENTS.read_text(encoding="utf-8")
    if "streamlit" not in text.lower():
        if text and not text.endswith("\n"):
            text += "\n"
        text += "streamlit>=1.40\n"
        REQUIREMENTS.write_text(text, encoding="utf-8")


def _ensure_pyproject_dependency() -> None:
    if not PYPROJECT.exists():
        return

    text = PYPROJECT.read_text(encoding="utf-8")
    if "streamlit" in text.lower():
        return

    marker = '    "pillow>=10",\n'
    if marker in text:
        text = text.replace(marker, marker + '    "streamlit>=1.40",\n')
        PYPROJECT.write_text(text, encoding="utf-8")


def _update_readme() -> None:
    if not README.exists():
        return

    text = README.read_text(encoding="utf-8")

    if "## Live demo" not in text:
        marker = "---\n\n## Why this repository matters"
        if marker in text:
            text = text.replace(marker, README_SECTION + "\n## Why this repository matters")
        else:
            text = text.replace(
                "> The package is suitable for public demonstration and software review. It is not a drop-in replacement for the original operational system.",
                "> The package is suitable for public demonstration and software review. It is not a drop-in replacement for the original operational system.\n\n---\n\n"
                + README_SECTION,
            )

    live_note = "Live-demo scope and deployment notes are available in [docs/live_demo.md](docs/live_demo.md)."
    if live_note not in text:
        case_link = "For a short explanation of the private-to-public conversion strategy and engineering workflow, see [docs/case_study.md](docs/case_study.md)."
        if case_link in text:
            text = text.replace(case_link, case_link + "\n\n" + live_note)

    README.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
