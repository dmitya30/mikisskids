#!/usr/bin/env python3

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import sys


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://mikisskids.ru"


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.base_href = None
        self.references = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)

        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)

        element_name = values.get("name")
        if tag == "a" and element_name:
            self.ids.add(element_name)

        if tag == "base" and self.base_href is None:
            self.base_href = values.get("href")
            return

        attributes = {
            "a": ("href",),
            "link": ("href",),
            "script": ("src",),
            "img": ("src",),
            "source": ("src",),
            "video": ("src", "poster"),
            "form": ("action",),
        }

        for attribute in attributes.get(tag, ()):
            value = values.get(attribute)
            if value:
                self.references.append((tag, attribute, value))


def public_url(path):
    relative = path.relative_to(ROOT).as_posix()

    if relative == "index.html":
        return ORIGIN + "/"

    if relative.endswith("/index.html"):
        return ORIGIN + "/" + relative[:-10]

    return ORIGIN + "/" + relative


def target_file(url_path):
    decoded = unquote(url_path)
    relative = decoded.lstrip("/")
    candidate = (ROOT / relative).resolve()

    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None

    if candidate.is_dir():
        candidate = candidate / "index.html"

    if candidate.is_file():
        return candidate

    if not candidate.suffix:
        index_candidate = candidate / "index.html"
        if index_candidate.is_file():
            return index_candidate

    return None


def parse_document(path, cache):
    path = path.resolve()

    if path not in cache:
        parser = DocumentParser()
        parser.feed(path.read_text(encoding="utf-8"))
        cache[path] = parser

    return cache[path]


def main():
    html_files = sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts
    )

    cache = {}
    errors = []
    checked = 0

    for source in html_files:
        parser = parse_document(source, cache)
        document_url = public_url(source)
        base_url = urljoin(
            document_url,
            parser.base_href or document_url,
        )

        for tag, attribute, reference in parser.references:
            stripped = reference.strip()

            if not stripped:
                continue

            scheme = urlsplit(stripped).scheme.lower()
            if scheme in {
                "mailto",
                "tel",
                "javascript",
                "data",
                "blob",
            }:
                continue

            resolved = urljoin(base_url, stripped)
            parts = urlsplit(resolved)

            if parts.netloc and parts.netloc != "mikisskids.ru":
                continue

            checked += 1
            target = target_file(parts.path)

            if target is None:
                errors.append(
                    f"{source.relative_to(ROOT)}: "
                    f"{tag}[{attribute}]={reference!r} "
                    f"→ отсутствует {parts.path}"
                )
                continue

            if parts.fragment and target.suffix.lower() == ".html":
                target_parser = parse_document(target, cache)

                if unquote(parts.fragment) not in target_parser.ids:
                    errors.append(
                        f"{source.relative_to(ROOT)}: "
                        f"{tag}[{attribute}]={reference!r} "
                        f"→ отсутствует #{unquote(parts.fragment)} "
                        f"в {target.relative_to(ROOT)}"
                    )

    print(f"HTML-файлов: {len(html_files)}")
    print(f"Локальных ссылок и ресурсов проверено: {checked}")

    if errors:
        print("\nОбнаружены ошибки:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Internal links audit: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
