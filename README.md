# Python Web Scraping Interview Assignment

## 1. Overview

This project implements an ETL-style Python web scraping pipeline for the two public practice websites required by the assignment:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline extracts records, cleans and standardizes them, validates them, removes duplicates, and writes a consolidated CSV plus a JSON summary and execution log.

## 2. Python Version

Developed for Python 3.12.x.

## 3. Installation

Open a terminal in the project folder and run:

```bash
python -m pip install -r requirements.txt
```

## 4. Run

```bash
python main.py
```

The scraper follows the `Next` link on each website until there is no next link. It does not hard-code a page count.

## 5. Project Structure

```text
scraping_assignment/
├── scrapers/
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── output/
├── logs/
├── tests/
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## 6. Data Model

The common schema is:

- `source`
- `source_url`
- `name_or_title`
- `category`
- `price`
- `rating`
- `author`
- `tags`
- `description`
- `scraped_at`

Fields that do not apply to a source are stored as empty/null values rather than invented data.

For Books to Scrape, `name_or_title` is the book title, `category` is `Books`, `price` is numeric, and `rating` is converted from the site's word-based star rating.

For Quotes to Scrape, `name_or_title` contains the quote text, `author` contains the quote author, and `tags` contains the tags separated by commas.

## 7. Pagination

Each scraper starts from the source's first page. After parsing a page, it searches for `li.next a[href]`. If found, the relative link is converted to an absolute URL with `urljoin` and the loop continues. When the next link is absent, pagination ends.

## 8. Cleaning

Cleaning is kept separate from scraping. The pipeline:

- removes repeated/leading/trailing whitespace;
- converts non-breaking spaces to normal spaces;
- converts prices such as `£51.77` to `51.77`;
- converts ratings such as `Three` to `3`;
- normalizes missing values;
- checks that source URLs are HTTP/HTTPS URLs.

## 9. Validation

A record is rejected if it has an unknown source, no title/quote text, an invalid source URL, an invalid price, a rating outside 1-5, or (for quotes) no author.

Validation failures are counted by reason and logged. One bad record does not stop the complete run.

## 10. Deduplication

Duplicate keys use normalized `source`, `name_or_title`, and `author`. Text is case-folded, trimmed, and repeated whitespace is collapsed. Therefore values such as `Example Book`, ` Example Book `, and `EXAMPLE   BOOK` are treated as equivalent within the same source.

Duplicates are removed before writing the final CSV, and the number removed is included in `summary_report.json`.

## 11. Error Handling

Requests use a timeout and up to three attempts with exponential backoff. HTTP and connection errors are logged. If a page cannot be retrieved after retries, the scraper logs the failure and continues with the other source. Missing HTML elements are handled without crashing the entire run.

## 12. Outputs

After a successful run:

- `output/final_dataset.csv` — consolidated valid unique records.
- `output/summary_report.json` — pages, scraped, cleaned, rejected, rejection reasons, duplicate count, final count, and execution time.
- `logs/scraper.log` — timestamped requests, page progress, warnings, errors, and output information.

## 13. Testing

The tests are offline unit tests for cleaning, validation, and deduplication:

```bash
python -m unittest discover -s tests -v
```

The full scraper is run separately with:

```bash
python main.py
```

## 14. Assumptions

- The provided websites remain publicly accessible and retain the expected practice-site HTML structure.
- Empty source-specific fields are represented as empty strings or null values.
- Deduplication is intended to remove equivalent records within a source; source information remains part of the duplicate key.

## 15. Known Limitations

- The scraper depends on the current HTML structure of the two practice sites.
- The assignment does not require a database, Docker setup, asynchronous scraping, or checkpoint/resume functionality, so those features were not added.
- The project intentionally uses a small request delay rather than aggressive parallel requests.

## 16. AI Usage

See `AI_USAGE.md` for the required AI-use disclosure.
