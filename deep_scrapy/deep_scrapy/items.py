# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ThreadItem(scrapy.Item):
    thread_name = scrapy.Field()
    thread_link = scrapy.Field()
    thread_author = scrapy.Field()
    create_date = scrapy.Field()
    last_message = scrapy.Field()
    thread = scrapy.Field()
    
class PostItem(scrapy.Item):
    post_link = scrapy.Field()
    post_author = scrapy.Field()
    post_message = scrapy.Field()
    post_datetime = scrapy.Field()
    post = scrapy.Field()