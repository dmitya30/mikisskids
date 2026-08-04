#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def main():
    errors = []
    files = sorted(DOCS.rglob("*.md"))

    for path in files:
        text = path.read_text(encoding="utf-8")

        for number, line in enumerate(text.splitlines(), start=1):
            if line != line.rstrip():
                errors.append(
                    f"{path.relative_to(ROOT)}:{number}: "
                    "trailing whitespace"
                )

            if "\x00" in line:
                errors.append(
                    f"{path.relative_to(ROOT)}:{number}: NUL byte"
                )

        if text and not text.endswith("\n"):
            errors.append(
                f"{path.relative_to(ROOT)}: missing final newline"
            )

    print(f"Markdown-файлов проверено: {len(files)}")

    if errors:
        print("\nОбнаружены ошибки:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Markdown audit: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
