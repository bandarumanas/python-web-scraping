import csv
import json
import logging
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests

from processing.cleaning import clean_record
from processing.deduplication import deduplicate
from processing.validation import validate_record
from scrapers.books_scraper import START_URL as BOOKS_URL, parse_books
from scrapers.quotes_scraper import START_URL as QUOTES_URL, parse_quotes


OUTPUT_DIR = "output"
LOG_DIR = "logs"
CSV_PATH = os.path.join(OUTPUT_DIR, "final_dataset.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "summary_report.json")
LOG_PATH = os.path.join(LOG_DIR, "scraper.log")

FIELDS = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "scraped_at"
]


def configure_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def fetch(session, url, retries=3):
    """Fetch a page with a small exponential-backoff retry."""
    for attempt in range(1, retries + 1):
        try:
            logging.info("REQUEST %s (attempt %d)", url, attempt)
            response = session.get(url, timeout=20)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            logging.warning("Request failed for %s: %s", url, exc)
            if attempt == retries:
                logging.error("Giving up on %s after %d attempts", url, retries)
                return None
            time.sleep(2 ** (attempt - 1))
    return None


def scrape_source(session, source, start_url, parser):
    raw_records = []
    pages = 0
    current_url = start_url
    seen_pages = set()

    while current_url and current_url not in seen_pages:
        seen_pages.add(current_url)
        response = fetch(session, current_url)
        if response is None:
            break

        pages += 1
        try:
            records, next_url = parser(response.text, response.url)
            raw_records.extend(records)
            logging.info("PAGE %d | %s | records=%d", pages, source, len(records))
            if next_url:
                logging.info("NEXT %s -> %s", source, next_url)
            else:
                logging.info("END %s | no next link", source)
            current_url = next_url
        except Exception as exc:
            logging.exception("Parsing failed for %s: %s", current_url, exc)
            break

        # Be polite to the public practice sites.
        time.sleep(0.25)

    return raw_records, pages


def process_source(records, source):
    cleaned = []
    rejected = Counter()
    rejected_records = 0

    for raw in records:
        try:
            record = clean_record(raw)
            valid, reasons = validate_record(record)
            if valid:
                cleaned.append(record)
            else:
                rejected_records += 1
                for reason in reasons:
                    rejected[reason] += 1
                logging.warning("REJECTED %s record: %s", source, "; ".join(reasons))
        except Exception as exc:
            rejected_records += 1
            rejected["processing error"] += 1
            logging.exception("Processing error for %s: %s", source, exc)

    return cleaned, rejected, rejected_records


def write_csv(records):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)


def build_summary(source_stats, final_records, duplicates, started_at, finished_at):
    summary = {
        "started_at": started_at,
        "finished_at": finished_at,
        "execution_time_seconds": round(
            (datetime.fromisoformat(finished_at) - datetime.fromisoformat(started_at)).total_seconds(), 2
        ),
        "sources": source_stats,
        "duplicate_records_removed": len(duplicates),
        "final_record_count": len(final_records),
    }
    return summary


def write_summary(summary):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)


def main():
    configure_logging()
    started_at = datetime.now(timezone.utc).isoformat()
    logging.info("SCRAPER START")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Realisieren-Technologies-Assignment-Scraper/1.0",
        "Accept": "text/html,application/xhtml+xml",
    })

    source_configs = [
        ("Books to Scrape", BOOKS_URL, parse_books),
        ("Quotes to Scrape", QUOTES_URL, parse_quotes),
    ]

    all_cleaned = []
    source_stats = {}

    for source, start_url, parser in source_configs:
        raw, pages = scrape_source(session, source, start_url, parser)
        cleaned, rejected, rejected_records = process_source(raw, source)
        all_cleaned.extend(cleaned)
        source_stats[source] = {
            "pages_processed": pages,
            "scraped": len(raw),
            "cleaned": len(cleaned),
            "rejected": rejected_records,
            "rejected_by_reason": dict(rejected),
        }
        logging.info(
            "SOURCE SUMMARY | %s | scraped=%d cleaned=%d rejected=%d",
            source, len(raw), len(cleaned), rejected_records
        )

    final_records, duplicates = deduplicate(all_cleaned)
    if duplicates:
        logging.info("DEDUPLICATION | removed=%d", len(duplicates))

    write_csv(final_records)
    finished_at = datetime.now(timezone.utc).isoformat()
    summary = build_summary(source_stats, final_records, duplicates, started_at, finished_at)
    write_summary(summary)

    logging.info("OUTPUT CSV: %s", CSV_PATH)
    logging.info("OUTPUT JSON: %s", JSON_PATH)
    logging.info("FINAL RECORD COUNT: %d", len(final_records))
    logging.info("SCRAPER COMPLETE")


if __name__ == "__main__":
    main()
