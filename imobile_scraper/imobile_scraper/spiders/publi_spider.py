import scrapy

from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone

from imobile_scraper.items import PubliItem


class PubliSpider(scrapy.Spider):
    """
    Spider to scrape apartment listings from publi24.ro.
    """
    name = "publi"
    allowed_domains = ["publi24.ro"]
    start_urls = ["https://www.publi24.ro/anunturi/imobiliare/de-vanzare/apartamente/"]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 2,
        "FEEDS": {
            f"data/raw/publi_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}.json": {
                "format": "json",
                "encoding": "utf8",
            },
        },
    }

    def parse(self, response):

        # --- SCRAPE DATA ---
        for card in response.css("div.article-item"):
            item = PubliItem()

            item["source"] = ("publi",)
            item["id"] = (card.attrib.get("data-articleid"),)
            item["title"] = (card.css("h2.article-title a::text").get(),)
            item["description"] = (
                " ".join(card.css("p.article-description::text").getall()).strip(),
            )
            item["price"] = (
                card.css("div.article-info span.article-price::text").get(),
            )
            item["unit_price_surface"] = (
                card.css("p.article-short-info span.article-lbl-txt")
                .xpath("string()")
                .get(),
            )
            item["location"] = (card.css("p.article-location span::text").get(),)
            item["date_posted"] = (card.css("p.article-date span::text").get(),)
            item["scraped_at"] = datetime.now(timezone.utc).isoformat()

            yield item

        # --- PAGINATION ---
        # Only do this once on the first page.
        if "pag=" not in response.url:
            # Extract last page from pagination.
            all_links = response.css("ul.pagination li a::attr(href)").getall()
            last_page_num = 1
            for link in all_links:
                parsed = urlparse(link)
                q = parse_qs(parsed.query)
                if "pag" in q:
                    num = int(q["pag"][0])
                    if num > last_page_num:
                        last_page_num = num

            # Generate requests for all pages.
            for page_num in range(2, last_page_num + 1):
                url = f"https://www.publi24.ro/anunturi/imobiliare/de-vanzare/apartamente/?pag={page_num}"
                yield response.follow(url, callback=self.parse)
