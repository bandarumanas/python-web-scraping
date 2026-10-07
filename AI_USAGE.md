# AI_USAGE.md

## Tool Used

**Tool:** ChatGPT

## How it was used

ChatGPT was used to:

- understand the assignment requirements and organize the implementation;
- design the common data model for both sources;
- create an initial Requests + BeautifulSoup scraping structure;
- design next-link pagination;
- suggest reusable cleaning, validation, and deduplication functions;
- add retry/error-handling and logging logic;
- create unit tests for processing functions;
- draft the README and project documentation.

## Representative Prompts

1. "Help me build the Python web scraping assignment using Books to Scrape and Quotes to Scrape with pagination, cleaning, validation, deduplication, logging, CSV and JSON outputs."
2. "Create a common schema for the book and quote records without inventing source-specific data."
3. "Add validation, duplicate detection that handles whitespace/capitalization differences, and error handling without stopping the full scraper."
4. "Create README and AI usage documentation that match the assignment requirements."

## AI-Assisted Parts

The initial implementation structure and documentation were AI-assisted. The candidate is responsible for reviewing the generated code, installing its dependencies, running the tests and scraper, checking the generated CSV/JSON/log files, and correcting any issues found during execution.

## Important Verification

The solution is designed around the assignment's required behavior: follow the websites' next links instead of hard-coding a page count, keep scraping separate from processing, validate before writing the final dataset, measure duplicates, and continue after reasonable request failures.

Before submission, the candidate should run:

```bash
python -m unittest discover -s tests -v
python main.py
```

The generated output files should then be inspected before creating the final ZIP.
