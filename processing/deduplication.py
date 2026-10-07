import re


def normalize_key(value):
    """Normalize text so spacing/capitalization differences do not defeat deduplication."""
    value = str(value or "").replace("\xa0", " ").strip().casefold()
    return re.sub(r"\s+", " ", value)


def record_key(record):
    return (
        normalize_key(record.get("source")),
        normalize_key(record.get("name_or_title")),
        normalize_key(record.get("author")),
    )


def deduplicate(records):
    unique = []
    duplicate_records = []
    seen = set()

    for record in records:
        key = record_key(record)
        if key in seen:
            duplicate_records.append(record)
        else:
            seen.add(key)
            unique.append(record)

    return unique, duplicate_records
