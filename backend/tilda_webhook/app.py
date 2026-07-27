#!/usr/bin/env python3
"""Minimal Tilda Webhook receiver for MIKISSKIDS."""

from __future__ import annotations

import hmac
import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8091
DEFAULT_MAX_BODY_BYTES = 65536
DEFAULT_DB_PATH = "/var/lib/mikisskids/orders.sqlite3"

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

REDACTED_KEY_PARTS = (
    "cookie",
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "card",
    "pan",
    "cvv",
    "cvc",
)


def get_required_secret() -> str:
    secret = os.environ.get("WEBHOOK_SECRET", "").strip()

    if len(secret) < 32:
        raise RuntimeError(
            "WEBHOOK_SECRET must contain at least 32 characters"
        )

    if "replace" in secret.casefold() or "example" in secret.casefold():
        raise RuntimeError("WEBHOOK_SECRET contains a placeholder")

    return secret


def get_db_path() -> Path:
    return Path(os.environ.get("DB_PATH", DEFAULT_DB_PATH))


def get_max_body_bytes() -> int:
    value = int(
        os.environ.get("MAX_BODY_BYTES", str(DEFAULT_MAX_BODY_BYTES))
    )

    if value < 1024 or value > 1048576:
        raise RuntimeError(
            "MAX_BODY_BYTES must be between 1024 and 1048576"
        )

    return value


def connect_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA foreign_keys = ON")

    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)

    return connection


@contextmanager
def open_database(db_path: Path):
    connection = connect_database(db_path)

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def parse_form_body(body: bytes) -> dict[str, object]:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("request body must be UTF-8") from error

    try:
        parsed = parse_qs(
            text,
            keep_blank_values=True,
            strict_parsing=False,
            max_num_fields=200,
        )
    except ValueError as error:
        raise ValueError("invalid form payload") from error

    result: dict[str, object] = {}

    for key, values in parsed.items():
        clean_key = key.strip()

        if not clean_key:
            continue

        if len(values) == 1:
            result[clean_key] = values[0].strip()
        else:
            result[clean_key] = [
                value.strip()
                for value in values
            ]

    return result


def first_value(
    payload: dict[str, object],
    *aliases: str,
) -> str:
    normalized = {
        key.casefold().strip(): value
        for key, value in payload.items()
    }

    for alias in aliases:
        value = normalized.get(alias.casefold().strip())

        if isinstance(value, list):
            value = value[0] if value else ""

        if value is not None and str(value).strip():
            return str(value).strip()

    return ""


def extract_products(payload: dict[str, object]) -> str:
    direct = first_value(
        payload,
        "product",
        "products",
        "товар",
        "товары",
        "payment.products",
        "payment[products]",
    )

    if direct:
        return direct

    product_fields = {
        key: value
        for key, value in payload.items()
        if key.casefold().startswith("payment[products]")
        or key.casefold().startswith("payment.products")
    }

    if not product_fields:
        return ""

    return json.dumps(
        product_fields,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def is_sensitive_key(key: str) -> bool:
    normalized = key.casefold()

    return any(
        part in normalized
        for part in REDACTED_KEY_PARTS
    )


def sanitized_payload(
    payload: dict[str, object],
) -> dict[str, object]:
    return {
        key: value
        for key, value in payload.items()
        if not is_sensitive_key(key)
    }


def validate_text(
    value: str,
    field: str,
    max_length: int,
) -> str:
    if len(value) > max_length:
        raise ValueError(f"{field} is too long")

    return value


def save_order(
    db_path: Path,
    payload: dict[str, object],
    source_url: str = "",
) -> bool:
    tranid = validate_text(
        first_value(payload, "tranid"),
        "tranid",
        128,
    )

    if not tranid:
        raise ValueError("tranid is required")

    formid = validate_text(
        first_value(payload, "formid"),
        "formid",
        128,
    )

    tilda_order_id = validate_text(
        first_value(
            payload,
            "payment.orderid",
            "payment[orderid]",
            "orderid",
        ),
        "tilda_order_id",
        256,
    )

    product_text = validate_text(
        extract_products(payload),
        "product_text",
        10000,
    )

    amount_text = validate_text(
        first_value(
            payload,
            "payment.amount",
            "payment[amount]",
            "amount",
            "total",
            "sum",
            "сумма",
        ),
        "amount_text",
        128,
    )

    customer_name = validate_text(
        first_value(payload, "name", "имя"),
        "customer_name",
        512,
    )

    phone = validate_text(
        first_value(payload, "phone", "телефон"),
        "phone",
        128,
    )

    email = validate_text(
        first_value(
            payload,
            "email",
            "e-mail",
            "почта",
        ),
        "email",
        512,
    )

    city = validate_text(
        first_value(payload, "city", "город"),
        "city",
        512,
    )

    comment = validate_text(
        first_value(
            payload,
            "comment",
            "comments",
            "комментарий",
        ),
        "comment",
        5000,
    )

    source_url = validate_text(
        source_url,
        "source_url",
        2048,
    )

    clean_payload = sanitized_payload(payload)
    raw_payload_json = json.dumps(
        clean_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    received_at = datetime.now(timezone.utc).isoformat()

    with open_database(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO orders (
                tranid,
                received_at,
                formid,
                tilda_order_id,
                product_text,
                amount_text,
                customer_name,
                phone,
                email,
                city,
                comment,
                source_url,
                status,
                raw_payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tranid,
                received_at,
                formid,
                tilda_order_id,
                product_text,
                amount_text,
                customer_name,
                phone,
                email,
                city,
                comment,
                source_url,
                "paid_reported_by_tilda",
                raw_payload_json,
            ),
        )

        return cursor.rowcount == 1


class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "MIKISSKIDSWebhook/1.0"
    sys_version = ""

    def log_message(
        self,
        format: str,
        *args: object,
    ) -> None:
        return

    def send_plain(
        self,
        status: int,
        text: str,
        *,
        allow: str | None = None,
    ) -> None:
        body = text.encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.send_header(
            "Cache-Control",
            "no-store",
        )
        self.send_header(
            "X-Content-Type-Options",
            "nosniff",
        )

        if allow:
            self.send_header("Allow", allow)

        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self.send_plain(
            405,
            "Method Not Allowed",
            allow="POST",
        )

    def do_HEAD(self) -> None:
        self.send_plain(
            405,
            "Method Not Allowed",
            allow="POST",
        )

    def do_POST(self) -> None:
        try:
            self.handle_webhook()
        except BrokenPipeError:
            return
        except Exception as error:
            print(
                f"webhook error: {type(error).__name__}",
                file=sys.stderr,
                flush=True,
            )
            self.send_plain(
                500,
                "Internal Server Error",
            )

    def handle_webhook(self) -> None:
        expected_secret = get_required_secret()
        request_path = urlsplit(self.path).path
        expected_path = (
            f"/api/tilda/paid/{expected_secret}"
        )

        if not hmac.compare_digest(
            request_path,
            expected_path,
        ):
            self.send_plain(404, "Not Found")
            return

        content_type = self.headers.get(
            "Content-Type",
            "",
        ).split(";", 1)[0].strip().casefold()

        if (
            content_type
            != "application/x-www-form-urlencoded"
        ):
            self.send_plain(
                415,
                "Unsupported Media Type",
            )
            return

        content_length_text = self.headers.get(
            "Content-Length"
        )

        if content_length_text is None:
            self.send_plain(411, "Length Required")
            return

        try:
            content_length = int(content_length_text)
        except ValueError:
            self.send_plain(400, "Bad Request")
            return

        max_body_bytes = get_max_body_bytes()

        if content_length < 0:
            self.send_plain(400, "Bad Request")
            return

        if content_length > max_body_bytes:
            self.send_plain(413, "Payload Too Large")
            return

        body = self.rfile.read(content_length)

        if len(body) != content_length:
            self.send_plain(400, "Bad Request")
            return

        try:
            payload = parse_form_body(body)
            source_url = self.headers.get("Referer", "")
            save_order(
                get_db_path(),
                payload,
                source_url,
            )
        except ValueError:
            self.send_plain(400, "Bad Request")
            return

        self.send_plain(200, "OK")


def main() -> None:
    get_required_secret()
    db_path = get_db_path()

    with open_database(db_path):
        pass

    host = os.environ.get(
        "BIND_HOST",
        DEFAULT_HOST,
    )
    port = int(
        os.environ.get(
            "PORT",
            str(DEFAULT_PORT),
        )
    )

    server = ThreadingHTTPServer(
        (host, port),
        WebhookHandler,
    )

    print(
        f"webhook receiver started on {host}:{port}",
        flush=True,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
