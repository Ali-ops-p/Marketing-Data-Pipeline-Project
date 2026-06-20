"""Convert TweetClaw exports into review rows for sentiment enrichment."""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

TEXT_FIELDS = ("text", "tweet_text", "tweet", "full_text", "content", "body")
DATE_FIELDS = ("created_at", "createdAt", "timestamp", "date")
ID_FIELDS = ("id", "tweet_id", "tweetId", "post_id")
AUTHOR_FIELDS = ("author_id", "author", "username", "screen_name", "user")
FIELDNAMES = ("ReviewID", "CustomerID", "ProductID", "ReviewDate", "Rating", "ReviewText")


def read_rows(path):
    """Read TweetClaw JSON, JSONL, NDJSON, or CSV rows."""
    content = Path(path).read_text(encoding="utf-8-sig").strip()
    if not content:
        return []

    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return _read_csv(content)
    if suffix in (".jsonl", ".ndjson"):
        return _read_json_lines(content)

    if content[0] in "[{":
        payload = json.loads(content)
        rows = _extract_rows(payload)
        return [row for row in rows if isinstance(row, dict)]

    return _read_json_lines(content)


def convert_rows(rows, default_product_id="0", default_rating="3"):
    """Yield rows compatible with the existing customer review pipeline."""
    review_number = 1
    for row in rows:
        text = _first_string(row, TEXT_FIELDS)
        if text is None:
            continue

        yield {
            "ReviewID": _first_string(row, ID_FIELDS) or str(review_number),
            "CustomerID": _first_string(row, AUTHOR_FIELDS) or "tweetclaw",
            "ProductID": default_product_id,
            "ReviewDate": _format_review_date(_first_string(row, DATE_FIELDS)),
            "Rating": default_rating,
            "ReviewText": text,
        }
        review_number += 1


def write_review_csv(rows, output_path):
    """Write semicolon-delimited review rows for SQL Server import."""
    with Path(output_path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(content):
    sample = content.splitlines()[0]
    delimiter = ";" if sample.count(";") > sample.count(",") else ","
    return [dict(row) for row in csv.DictReader(content.splitlines(), delimiter=delimiter)]


def _read_json_lines(content):
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _extract_rows(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("results", "tweets", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return [payload]

    return []


def _first_string(row, fields):
    for field in fields:
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dict):
            nested = _first_string(value, ("id", "username", "screen_name", "name"))
            if nested:
                return nested
    return None


def _format_review_date(value):
    if not value:
        return ""

    for pattern in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, pattern).strftime("%d.%m.%Y")
        except ValueError:
            continue

    return value


def main():
    parser = argparse.ArgumentParser(
        description="Convert TweetClaw exports into customer review CSV rows."
    )
    parser.add_argument("input", help="TweetClaw JSON, JSONL, NDJSON, or CSV export.")
    parser.add_argument(
        "--output",
        default="tweetclaw_customer_reviews.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--product-id",
        default="0",
        help="ProductID to assign to imported social listening rows.",
    )
    parser.add_argument(
        "--rating",
        default="3",
        help="Neutral placeholder rating for social listening rows.",
    )
    args = parser.parse_args()

    rows = convert_rows(
        read_rows(args.input),
        default_product_id=args.product_id,
        default_rating=args.rating,
    )
    write_review_csv(rows, args.output)


if __name__ == "__main__":
    main()
