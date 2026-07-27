#!/usr/bin/env python3

from pathlib import Path
import json
import re
import sys

errors = []

targets = {
    Path("index.html"): {
        "types": {"Organization", "WebSite"},
    },
    Path("chair/index.html"): {
        "types": {"Organization", "Product"},
        "price": 35000,
        "currency": "RUB",
        "url": "https://mikisskids.ru/chair/",
    },
    Path("travel-seat/index.html"): {
        "types": {"Organization", "Product"},
        "price": 50000,
        "currency": "RUB",
        "url": "https://mikisskids.ru/travel-seat/",
    },
}

pattern = re.compile(
    r'<script\s+type="application/ld\+json">\s*'
    r'(.*?)\s*</script>',
    re.DOTALL,
)

for path, expected in targets.items():
    text = path.read_text(encoding="utf-8")
    matches = pattern.findall(text)

    if len(matches) != 1:
        errors.append(
            f"{path}: JSON-LD blocks found: {len(matches)}, expected 1"
        )
        continue

    try:
        data = json.loads(matches[0])
    except json.JSONDecodeError as error:
        errors.append(f"{path}: invalid JSON-LD: {error}")
        continue

    if data.get("@context") != "https://schema.org":
        errors.append(f"{path}: incorrect @context")

    graph = data.get("@graph")

    if not isinstance(graph, list):
        errors.append(f"{path}: @graph must be a list")
        continue

    found_types = {
        item.get("@type")
        for item in graph
        if isinstance(item, dict)
    }

    missing = expected["types"] - found_types

    if missing:
        errors.append(
            f"{path}: missing schema types: {sorted(missing)}"
        )

    if "price" not in expected:
        continue

    products = [
        item for item in graph
        if isinstance(item, dict)
        and item.get("@type") == "Product"
    ]

    if len(products) != 1:
        errors.append(
            f"{path}: Product objects found: {len(products)}, expected 1"
        )
        continue

    product = products[0]
    offers = product.get("offers")

    if not isinstance(offers, dict):
        errors.append(f"{path}: Product.offers is missing")
        continue

    checks = {
        "@type": "Offer",
        "price": expected["price"],
        "priceCurrency": expected["currency"],
        "url": expected["url"],
    }

    for key, expected_value in checks.items():
        actual = offers.get(key)

        if actual != expected_value:
            errors.append(
                f"{path}: offers.{key}={actual!r}, "
                f"expected {expected_value!r}"
            )

    for field in ("name", "description", "image", "brand"):
        if not product.get(field):
            errors.append(f"{path}: Product.{field} is missing")

error_page = Path("404.html")

if not error_page.is_file():
    errors.append("404.html: file is missing")
else:
    error_text = error_page.read_text(encoding="utf-8")

    if '<meta name="robots" content="noindex, follow">' not in error_text:
        errors.append("404.html: noindex, follow is missing")

    if 'rel="canonical"' in error_text:
        errors.append("404.html: canonical must not be present")

    if error_text.count("<h1") != 1:
        errors.append("404.html: expected exactly one H1")

nginx_path = Path("deploy/nginx-static-errors.conf")

if not nginx_path.is_file():
    errors.append("deploy/nginx-static-errors.conf: file is missing")
else:
    nginx_text = nginx_path.read_text(encoding="utf-8")

    if "error_page 404 /404.html;" not in nginx_text:
        errors.append("Nginx snippet: error_page directive is missing")

    if "internal;" not in nginx_text:
        errors.append("Nginx snippet: internal directive is missing")

if errors:
    print("SEO audit errors:", file=sys.stderr)

    for error in errors:
        print(f"- {error}", file=sys.stderr)

    raise SystemExit(1)

print("Structured data: OK")
print("Custom 404 files: OK")
