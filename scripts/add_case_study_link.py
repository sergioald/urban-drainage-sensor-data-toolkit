"""Add a case-study link to README.md.

Run from the repository root:

    python scripts/add_case_study_link.py
"""

from pathlib import Path

README = Path("README.md")

LINK_TEXT = "For a short explanation of the private-to-public conversion strategy and engineering workflow, see [docs/case_study.md](docs/case_study.md)."


def main() -> None:
    text = README.read_text(encoding="utf-8")

    if LINK_TEXT in text:
        print("README already contains case-study link.")
        return

    anchor = "The project demonstrates how private operational monitoring workflows can be converted into a clean research-software package using synthetic examples, tests, documentation, and strict publication boundaries."
    replacement = anchor + "\n\n" + LINK_TEXT

    if anchor in text:
        text = text.replace(anchor, replacement)
    else:
        insert_after = "> The package is suitable for public demonstration and software review. It is not a drop-in replacement for the original operational system."
        text = text.replace(insert_after, insert_after + "\n\n" + LINK_TEXT)

    README.write_text(text, encoding="utf-8")
    print("Added case-study link to README.")


if __name__ == "__main__":
    main()
