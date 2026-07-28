#!/usr/bin/env python3

from pathlib import Path
import sys

errors = []
html_paths = sorted(Path(".").rglob("*.html"))

# Deployment snippets are not site pages.
html_paths = [
    path
    for path in html_paths
    if "deploy" not in path.parts
]

if len(html_paths) != 10:
    errors.append(
        f"HTML page count: {len(html_paths)}, expected 10"
    )

for path in html_paths:
    text = path.read_text(encoding="utf-8")

    if text.count('href="css/consent.css"') != 1:
        errors.append(f"{path}: consent.css missing or duplicated")

    if text.count('src="js/consent.js"') != 1:
        errors.append(f"{path}: consent.js missing or duplicated")

    consent_position = text.find('src="js/consent.js"')
    main_position = text.find('src="js/main.js"')

    if consent_position < 0 or main_position < 0:
        errors.append(f"{path}: JavaScript asset missing")
    elif consent_position > main_position:
        errors.append(f"{path}: consent.js must load before main.js")

    if "mc.yandex.ru" in text:
        errors.append(
            f"{path}: Metrica must not be embedded directly in HTML"
        )

consent_path = Path("js/consent.js")
consent_text = consent_path.read_text(encoding="utf-8")

required_consent_fragments = (
    'const COUNTER_ID = 111056887;',
    'const COOKIE_NAME = "mk_cookie_consent";',
    'Domain=.mikisskids.ru',
    '"https://mc.yandex.ru/metrika/tag.js"',
    'currentConsent() !== "accepted"',
    'data-cookie-accept',
    'data-cookie-reject',
    'data-cookie-settings',
    'webvisor: false',
)

for fragment in required_consent_fragments:
    if fragment not in consent_text:
        errors.append(f"js/consent.js: missing {fragment!r}")

main_text = Path("js/main.js").read_text(encoding="utf-8")

for fragment in (
    '"checkout_start"',
    "window.MikissConsent.reachGoal",
    "data-cookie-settings",
):
    if fragment not in main_text:
        errors.append(f"js/main.js: missing {fragment!r}")

privacy_text = Path(
    "legal/privacy/index.html"
).read_text(encoding="utf-8")

for fragment in (
    'id="cookies"',
    "111056887",
    "ООО «ЯНДЕКС»",
    "не загружается до получения",
    "Настройки cookies",
):
    if fragment not in privacy_text:
        errors.append(
            f"legal/privacy/index.html: missing {fragment!r}"
        )

snippet = Path("deploy/tilda-consent-head.html")

if not snippet.is_file():
    errors.append("Tilda consent snippet is missing")
else:
    snippet_text = snippet.read_text(encoding="utf-8")

    if "js/consent.js?v=1" not in snippet_text:
        errors.append("Tilda snippet: consent.js missing")

    if "css/consent.css?v=1" not in snippet_text:
        errors.append("Tilda snippet: consent.css missing")

if errors:
    print("Consent audit errors:", file=sys.stderr)

    for error in errors:
        print(f"- {error}", file=sys.stderr)

    raise SystemExit(1)

print("Consent-gated Yandex Metrica: OK")
print(f"HTML pages checked: {len(html_paths)}")
