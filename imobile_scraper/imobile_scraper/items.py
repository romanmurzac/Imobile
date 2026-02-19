import scrapy


class PubliItem(scrapy.Item):
    source = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    unit_price_surface = scrapy.Field()
    location = scrapy.Field()
    date_posted = scrapy.Field()
    scraped_at = scrapy.Field()
