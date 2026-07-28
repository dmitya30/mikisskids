#!/usr/bin/env python3

from pathlib import Path
from html.parser import HTMLParser
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
        "availability": "https://schema.org/InStock",
    },
    Path("travel-seat/index.html"): {
        "types": {"Organization", "Product"},
        "price": 50000,
        "currency": "RUB",
        "url": "https://mikisskids.ru/travel-seat/",
        "availability": "https://schema.org/PreOrder",
        "availability_starts": "2026-08-17",
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
        "availability": expected["availability"],
    }

    for key, expected_value in checks.items():
        actual = offers.get(key)

        if actual != expected_value:
            errors.append(
                f"{path}: offers.{key}={actual!r}, "
                f"expected {expected_value!r}"
            )

    if "availability_starts" in expected:
        actual_start = offers.get("availabilityStarts")

        if actual_start != expected["availability_starts"]:
            errors.append(
                f"{path}: offers.availabilityStarts={actual_start!r}, "
                f"expected {expected['availability_starts']!r}"
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


class MediaDimensionParser(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.images = []
        self.videos = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        line = self.getpos()[0]

        if tag == "img":
            self.images.append((line, attributes))

        if tag == "video":
            self.videos.append((line, attributes))


for html_path in sorted(Path(".").rglob("*.html")):
    if ".git" in html_path.parts:
        continue

    parser = MediaDimensionParser(html_path)
    parser.feed(html_path.read_text(encoding="utf-8"))

    for line, attributes in parser.images:
        src = attributes.get("src", "")
        width = attributes.get("width")
        height = attributes.get("height")

        if not width or not height:
            errors.append(
                f"{html_path}:{line}: image dimensions missing: {src}"
            )
            continue

        if not width.isdigit() or not height.isdigit():
            errors.append(
                f"{html_path}:{line}: non-integer image dimensions: "
                f"{src} ({width}x{height})"
            )

    for line, attributes in parser.videos:
        poster = attributes.get("poster", "")
        width = attributes.get("width")
        height = attributes.get("height")

        if not width or not height:
            errors.append(
                f"{html_path}:{line}: video dimensions missing: {poster}"
            )
            continue

        if not width.isdigit() or not height.isdigit():
            errors.append(
                f"{html_path}:{line}: non-integer video dimensions: "
                f"{poster} ({width}x{height})"
            )


hero_images = {
    Path("index.html"):
        "assets/images/chair/chair-01.jpg",
    Path("chair/index.html"):
        "assets/images/chair/chair-01.jpg",
    Path("travel-seat/index.html"):
        "assets/images/travel-seat/travel-seat-01.jpg",
}

for html_path, hero_src in hero_images.items():
    text = html_path.read_text(encoding="utf-8")

    match = re.search(
        r'<img\b[^>]*\bsrc="'
        + re.escape(hero_src)
        + r'"[^>]*>',
        text,
        re.DOTALL,
    )

    if not match:
        errors.append(
            f"{html_path}: hero image not found: {hero_src}"
        )
        continue

    hero_tag = match.group(0)

    if 'fetchpriority="high"' not in hero_tag:
        errors.append(
            f"{html_path}: hero image fetchpriority=high missing"
        )

    if 'loading="lazy"' in hero_tag:
        errors.append(
            f"{html_path}: hero image must not use lazy loading"
        )


expected_videos = {
    Path("chair/index.html"): (
        "assets/images/chair/chair-02.jpg",
        "1280",
        "720",
    ),
    Path("travel-seat/index.html"): (
        "assets/images/travel-seat/travel-seat-02.jpg",
        "848",
        "464",
    ),
}

for html_path, expected in expected_videos.items():
    poster, expected_width, expected_height = expected
    parser = MediaDimensionParser(html_path)
    parser.feed(html_path.read_text(encoding="utf-8"))

    matching = [
        attributes
        for _, attributes in parser.videos
        if attributes.get("poster") == poster
    ]

    if len(matching) != 1:
        errors.append(
            f"{html_path}: expected one video with poster {poster}, "
            f"found {len(matching)}"
        )
        continue

    attributes = matching[0]

    if attributes.get("width") != expected_width:
        errors.append(
            f"{html_path}: incorrect video width for {poster}"
        )

    if attributes.get("height") != expected_height:
        errors.append(
            f"{html_path}: incorrect video height for {poster}"
        )


js_path = Path("js/main.js")
js_text = js_path.read_text(encoding="utf-8")

js_image_tags = re.findall(
    r"<img\b.*?>",
    js_text,
    flags=re.IGNORECASE | re.DOTALL,
)

for index, tag in enumerate(js_image_tags, start=1):
    src_match = re.search(r'\bsrc="([^"]+)"', tag)
    width_match = re.search(r'\bwidth="([0-9]+)"', tag)
    height_match = re.search(r'\bheight="([0-9]+)"', tag)

    src = src_match.group(1) if src_match else f"image {index}"

    if not width_match or not height_match:
        errors.append(
            f"js/main.js: generated image dimensions missing: {src}"
        )


robots_path = Path("robots.txt")

if not robots_path.is_file():
    errors.append("robots.txt: file is missing")
else:
    robots_text = robots_path.read_text(encoding="utf-8")

    required_robots_directives = (
        "User-agent: *",
        "Disallow: /",
        "Allow: /sitemap.xml",
        "Sitemap: https://mikisskids.ru/sitemap.xml",
    )

    for directive in required_robots_directives:
        if directive not in robots_text:
            errors.append(
                f"robots.txt: missing directive: {directive}"
            )

sitemap_path = Path("sitemap.xml")

if not sitemap_path.is_file():
    errors.append("sitemap.xml: file is missing")
else:
    sitemap_text = sitemap_path.read_text(encoding="utf-8")

    expected_sitemap_urls = (
        "https://mikisskids.ru/",
        "https://mikisskids.ru/chair/",
        "https://mikisskids.ru/travel-seat/",
        "https://mikisskids.ru/about/",
        "https://mikisskids.ru/delivery/",
    )

    for url in expected_sitemap_urls:
        if f"<loc>{url}</loc>" not in sitemap_text:
            errors.append(f"sitemap.xml: missing URL: {url}")

    if sitemap_text.count("<lastmod>2026-07-28</lastmod>") != 5:
        errors.append(
            "sitemap.xml: expected five lastmod values for 2026-07-28"
        )



delivery_content_requirements = {
    Path("index.html"): (
        "Доставка по России включена в стоимость.",
    ),
    Path("chair/index.html"): (
        "https://schema.org/InStock",
        "<strong>В наличии.</strong>",
        "5 рабочих дней после оплаты",
    ),
    Path("travel-seat/index.html"): (
        "https://schema.org/PreOrder",
        '"availabilityStarts": "2026-08-17"',
        "<strong>Предзаказ.</strong>",
        "до 17 августа 2026 года",
    ),
    Path("delivery/index.html"): (
        "Доставка включена в стоимость товара",
        "в течение одного",
        "рабочего дня",
        "17 августа 2026 года",
    ),
    Path("legal/offer/index.html"): (
        "Редакция от 28 июля 2026 года.",
        "Доставка осуществляется по России.",
        "не позднее 17 августа 2026 года",
        "в течение одного",
        "рабочего дня",
    ),
}

for content_path, fragments in delivery_content_requirements.items():
    content_text = content_path.read_text(encoding="utf-8")

    for fragment in fragments:
        if fragment not in content_text:
            errors.append(
                f"{content_path}: delivery content missing: "
                f"{fragment!r}"
            )


if errors:
    print("SEO audit errors:", file=sys.stderr)

    for error in errors:
        print(f"- {error}", file=sys.stderr)

    raise SystemExit(1)

print("Structured data: OK")
print("Custom 404 files: OK")
