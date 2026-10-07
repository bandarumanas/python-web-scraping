from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup


SOURCE = "Quotes to Scrape"
START_URL = "https://quotes.toscrape.com/"


def parse_quotes(html, page_url):
    """Parse all quote cards from one page."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    scraped_at = datetime.now(timezone.utc).isoformat()

    for card in soup.select("div.quote"):
        try:
            text_node = card.select_one("span.text")
            author_node = card.select_one("small.author")
            tags = [tag.get_text(" ", strip=True) for tag in card.select("a.tag")]

            quote_text = text_node.get_text(" ", strip=True) if text_node else ""
            author = author_node.get_text(" ", strip=True) if author_node else ""

            rows.append({
                "source": SOURCE,
                "source_url": page_url,
                "name_or_title": quote_text,
                "category": "",
                "price": "",
                "rating": None,
                "author": author,
                "tags": ", ".join(tags),
                "description": quote_text,
                "scraped_at": scraped_at,
            })
        except Exception:
            continue

    next_link = soup.select_one("li.next a[href]")
    next_url = urljoin(page_url, next_link["href"]) if next_link else None
    return rows, next_url
