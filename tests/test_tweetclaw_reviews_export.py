"""Tests for TweetClaw review export conversion."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from tweetclaw_reviews_export import convert_rows, read_rows, write_review_csv


class TestTweetClawReviewsExport(unittest.TestCase):
    def test_jsonl_rows_convert_to_review_shape(self):
        rows = [
            {
                "tweet_id": "101",
                "text": "Campaign feedback looks strong",
                "created_at": "2026-06-20T14:00:00Z",
                "username": "market_user",
            },
            {"id": "102", "tweet": "Checkout friction is still painful", "author": {"id": "42"}},
        ]
        path = self._write_lines([json.dumps(row) for row in rows])

        converted = list(convert_rows(read_rows(path), default_product_id="7", default_rating="3"))

        self.assertEqual(converted[0]["ReviewID"], "101")
        self.assertEqual(converted[0]["CustomerID"], "market_user")
        self.assertEqual(converted[0]["ProductID"], "7")
        self.assertEqual(converted[0]["ReviewDate"], "20.06.2026")
        self.assertEqual(converted[1]["ReviewText"], "Checkout friction is still painful")
        self.assertEqual(converted[1]["CustomerID"], "42")

    def test_csv_rows_write_semicolon_review_file(self):
        input_path = self._write_lines(
            [
                "tweet_id,text,created_at,screen_name",
                "201,CSV social feedback,2026-06-20,csv_user",
            ],
            suffix=".csv",
        )
        output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name)

        write_review_csv(convert_rows(read_rows(input_path)), output_path)

        with output_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter=";"))

        self.assertEqual(rows[0]["ReviewID"], "201")
        self.assertEqual(rows[0]["ReviewText"], "CSV social feedback")

    def test_rows_without_text_are_skipped(self):
        converted = list(convert_rows([{"tweet_id": "empty"}]))

        self.assertEqual(converted, [])

    def _write_lines(self, lines, suffix=".jsonl"):
        handle = tempfile.NamedTemporaryFile("w", delete=False, suffix=suffix, encoding="utf-8")
        with handle:
            handle.write("\n".join(lines))
        return Path(handle.name)


if __name__ == "__main__":
    unittest.main()
