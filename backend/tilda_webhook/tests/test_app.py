import sqlite3
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode

from backend.tilda_webhook.app import (
    is_tilda_test_payload,
    parse_form_body,
    sanitized_payload,
    save_order,
)


class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = (
            Path(self.temp_dir.name)
            / "orders.sqlite3"
        )

        self.payload = {
            "tranid": "lead-10001",
            "formid": "form123",
            "name": "Тестовый Покупатель",
            "phone": "+79990000000",
            "email": "test@example.com",
            "city": "Москва",
            "comment": "Тестовая заявка",
            "payment[orderid]": "order-500",
            "payment[amount]": "35000",
            "payment[products][0][name]": (
                "Стульчик-трансформер MIKISSKIDS"
            ),
            "COOKIES": "must-not-be-stored",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_urlencoded_payload_is_decoded(self):
        body = urlencode(
            self.payload
        ).encode("utf-8")

        parsed = parse_form_body(body)

        self.assertEqual(
            parsed["email"],
            "test@example.com",
        )
        self.assertEqual(
            parsed["payment[amount]"],
            "35000",
        )

    def test_order_is_saved(self):
        created = save_order(
            self.db_path,
            self.payload,
            "https://pay.mikisskids.ru/payment-mvp",
        )

        self.assertTrue(created)

        connection = sqlite3.connect(
            self.db_path
        )
        row = connection.execute(
            """
            SELECT
                tranid,
                amount_text,
                product_text,
                status,
                raw_payload_json
            FROM orders
            """
        ).fetchone()
        connection.close()

        self.assertEqual(
            row[0],
            "lead-10001",
        )
        self.assertEqual(
            row[1],
            "35000",
        )
        self.assertIn(
            "Стульчик-трансформер",
            row[2],
        )
        self.assertEqual(
            row[3],
            "paid_reported_by_tilda",
        )
        self.assertNotIn(
            "must-not-be-stored",
            row[4],
        )

    def test_duplicate_tranid_is_idempotent(self):
        first = save_order(
            self.db_path,
            self.payload,
        )
        second = save_order(
            self.db_path,
            self.payload,
        )

        self.assertTrue(first)
        self.assertFalse(second)

        connection = sqlite3.connect(
            self.db_path
        )
        count = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]
        connection.close()

        self.assertEqual(count, 1)

    def test_tilda_order_id_is_fallback(self):
        payload = dict(self.payload)
        payload.pop("tranid")

        first = save_order(
            self.db_path,
            payload,
        )
        second = save_order(
            self.db_path,
            payload,
        )

        self.assertTrue(first)
        self.assertFalse(second)

        connection = sqlite3.connect(
            self.db_path
        )
        row = connection.execute(
            """
            SELECT
                tranid,
                tilda_order_id,
                COUNT(*)
            FROM orders
            """
        ).fetchone()
        connection.close()

        self.assertTrue(
            row[0].startswith("tilda-order:")
        )
        self.assertEqual(row[1], "order-500")
        self.assertEqual(row[2], 1)

    def test_payment_id_is_fallback(self):
        payload = dict(self.payload)
        payload.pop("tranid")
        payload.pop("payment[orderid]")
        payload["paymentid"] = "payment-700"

        created = save_order(
            self.db_path,
            payload,
        )

        self.assertTrue(created)

        connection = sqlite3.connect(
            self.db_path
        )
        tranid = connection.execute(
            "SELECT tranid FROM orders"
        ).fetchone()[0]
        connection.close()

        self.assertTrue(
            tranid.startswith("payment:")
        )

    def test_stable_identifier_is_required(self):
        payload = dict(self.payload)
        payload.pop("tranid")
        payload.pop("payment[orderid]")

        with self.assertRaisesRegex(
            ValueError,
            "stable order identifier is required",
        ):
            save_order(
                self.db_path,
                payload,
            )

    def test_tilda_connection_payload_is_recognized(self):
        self.assertTrue(
            is_tilda_test_payload({"test": "test"})
        )
        self.assertFalse(
            is_tilda_test_payload({
                "test": "test",
                "tranid": "unexpected",
            })
        )
        self.assertFalse(
            is_tilda_test_payload({"test": "other"})
        )

    def test_sensitive_fields_are_removed(self):
        payload = {
            "tranid": "1",
            "COOKIES": "private",
            "card_number": "private",
            "authorization": "private",
            "email": "allowed@example.com",
        }

        clean = sanitized_payload(payload)

        self.assertEqual(
            clean["tranid"],
            "1",
        )
        self.assertEqual(
            clean["email"],
            "allowed@example.com",
        )
        self.assertNotIn(
            "COOKIES",
            clean,
        )
        self.assertNotIn(
            "card_number",
            clean,
        )
        self.assertNotIn(
            "authorization",
            clean,
        )


if __name__ == "__main__":
    unittest.main()
