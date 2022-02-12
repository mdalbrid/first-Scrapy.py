import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item, Field
from deep_scrapy.items import DeepScrapyItem

from scrapy.loader.processors import MapCompose

class IsSpider(scrapy.Spider):
    name = 's'
    allowed_domains = ['s']
    start_urls = [
            'https://s/forums/',
            ]

    
    rules = (Rule(LinkExtractor(allow=('threads/\.+',), deny = ('index.php', 'search', 'tag', 'revblog_blog', 'jpg', 'png', 'page', 'uploads', 'autor', 'simpleregister', 'my_account', )), callback='parse', follow=True),)

    def parse(self, response):
        
        print("\n", "[ PROCESSING: "+response.url+" ]\n")
        
        thread = DeepScrapyItem()

        content = response.xpath('///div[@class="structItem-cell structItem-cell--main"]')


        for th in content:
            thread['link_thread'] = f"https://{self.name}" + th.xpath('./div[@class="structItem-title"]/a/@href').get()
            thread['name_thread'] = th.xpath('./div[@class="structItem-title"]/a/text()').get()
            thread['author_thread'] = th.xpath('.//a[@class="username "]/text()').get()
            thread['data_thread'] = th.xpath('.//time[@class="u-dt"]/@datetime').get()
            thread['last_message'] = th.xpath('..//time[@class="structItem-latestDate u-dt"]/@datetime').get()

            yield thread

