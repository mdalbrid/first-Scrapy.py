# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DeepScrapyItem(scrapy.Item):
    name_thread = scrapy.Field()
    link_thread = scrapy.Field()
    author_thread = scrapy.Field()
    data_thread = scrapy.Field()
    last_message = scrapy.Field()
    
