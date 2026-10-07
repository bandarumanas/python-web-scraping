import unittest

from processing.cleaning import clean_price, clean_rating, clean_text
from processing.deduplication import deduplicate
from processing.validation import validate_record


class TestProcessing(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text("  Example\xa0  Book  "), "Example Book")

    def test_clean_price(self):
        self.assertEqual(clean_price("£51.77"), 51.77)

    def test_clean_rating(self):
        self.assertEqual(clean_rating("Three"), 3)
        self.assertEqual(clean_rating(5), 5)

    def test_validation(self):
        record = {
            "source": "Books to Scrape",
            "source_url": "https://books.toscrape.com/catalogue/example.html",
            "name_or_title": "Example Book",
            "price": 10.5,
            "rating": 4,
        }
        self.assertTrue(validate_record(record)[0])

    def test_duplicate_normalization(self):
        records = [
            {"source": "Books to Scrape", "name_or_title": "Example Book", "author": ""},
            {"source": "Books to Scrape", "name_or_title": "  EXAMPLE   BOOK ", "author": ""},
        ]
        unique, duplicates = deduplicate(records)
        self.assertEqual(len(unique), 1)
        self.assertEqual(len(duplicates), 1)


if __name__ == "__main__":
    unittest.main()
