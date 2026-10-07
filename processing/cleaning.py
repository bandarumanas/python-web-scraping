import re
from urllib.parse import urlparse


RATING_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return ""
    value = str(value).replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def clean_price(value):
    if value is None or clean_text(value) == "":
        return None
    text = clean_text(value).replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def clean_rating(value):
    if value is None or clean_text(value) == "":
        return None
    if isinstance(value, (int, float)):
        return int(value) if 1 <= float(value) <= 5 else None
    text = clean_text(value).lower()
    if text in RATING_WORDS:
        return RATING_WORDS[text]
    match = re.fullmatch(r"[1-5](?:\.0)?", text)
    return int(float(match.group())) if match else None


def clean_url(value):
    value = clean_text(value)
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return ""


def clean_record(record):
    cleaned = dict(record)
    text_fields = [
        "source", "source_url", "name_or_title", "category",
        "author", "tags", "description", "scraped_at"
    ]
    for field in text_fields:
        cleaned[field] = clean_text(cleaned.get(field, ""))

    cleaned["price"] = clean_price(record.get("price"))
    cleaned["rating"] = clean_rating(record.get("rating"))
    cleaned["source_url"] = clean_url(cleaned["source_url"])
    return cleaned
