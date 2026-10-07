from urllib.parse import urlparse


def is_valid_url(value):
    try:
        parsed = urlparse(value or "")
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def validate_record(record):
    """Return (is_valid, list_of_reasons)."""
    reasons = []
    source = record.get("source", "")

    if source not in {"Books to Scrape", "Quotes to Scrape"}:
        reasons.append("unrecognized source")
    if not record.get("name_or_title"):
        reasons.append("missing name_or_title")
    if not is_valid_url(record.get("source_url")):
        reasons.append("invalid source_url")

    price = record.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        reasons.append("invalid price")

    rating = record.get("rating")
    if rating is not None and (not isinstance(rating, (int, float)) or not 1 <= rating <= 5):
        reasons.append("rating outside 1-5")

    if source == "Quotes to Scrape" and not record.get("author"):
        reasons.append("missing quote author")

    return not reasons, reasons
