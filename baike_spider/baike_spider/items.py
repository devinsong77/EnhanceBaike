# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BaikeItem(scrapy.Item):
    baike_id = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field()
    text = scrapy.Field()
    page_url = scrapy.Field()


class TriplesItem(scrapy.Item):
    triples_id = scrapy.Field()
    item_name = scrapy.Field()
    attr = scrapy.Field()
    value = scrapy.Field()
