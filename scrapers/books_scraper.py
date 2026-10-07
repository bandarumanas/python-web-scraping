from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup


SOURCE = "Books to Scrape"
START_URL = "https://books.toscrape.com/"


def parse_rating(classes):
    """Return the numeric star rating from a product's CSS classes."""
    rating_words = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for value in classes or []:
        if value in rating_words:
            return rating_words[value]
    return None


def parse_books(html, page_url):
    """Parse all book cards from one listing page."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    scraped_at = datetime.now(timezone.utc).isoformat()

    for card in soup.select("article.product_pod"):
        try:
            title_link = card.select_one("h3 a[href]")
            price_node = card.select_one("p.price_color")
            availability_node = card.select_one("p.instock.availability")
            rating_node = card.select_one("p.star-rating")

            title = title_link.get("title") if title_link else ""
            product_url = urljoin(page_url, title_link.get("href")) if title_link else ""
            price = price_node.get_text(" ", strip=True) if price_node else ""
            availability = availability_node.get_text(" ", strip=True) if availability_node else ""
            rating = parse_rating(rating_node.get("class", [])) if rating_node else None

            rows.append({
                "source": SOURCE,
                "source_url": product_url,
                "name_or_title": title,
                "category": "Books",
                "price": price,
                "rating": rating,
                "author": "",
                "tags": "",
                "description": "",
                "scraped_at": scraped_at,
            })
        except Exception:
            # Keep the page alive if one malformed card is encountered.
            continue

    next_link = soup.select_one("li.next a[href]")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return rows, next_url
