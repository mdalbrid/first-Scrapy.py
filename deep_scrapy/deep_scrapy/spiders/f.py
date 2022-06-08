#TODO: remove unused imports
import scrapy

import re
import logging
import datetime

import pathlib
import sys
import os
import argparse
import json

file = pathlib.Path(__file__)
sys.path.append(file.parents[2])

PROJECT_PATH = os.environ.get('PROJECT_PATH')
sys.path.append(str(PROJECT_PATH))

from common_libs.database import get_last_message
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item, Field
from deep_scrapy.items import ThreadItem, PostItem
from scrapy.crawler import CrawlerProcess

#from scddrapy.loader.processors import MapCompose
from scrapy.http import Request, FormRequest, HtmlResponse
#from scrapy.utils.response import open_in_browser
#from scrapy.selector import Selector
from dateutil.parser import parse


class FSpider(scrapy.Spider):
    name = 'f'
    allowed_domains = ['f']
    start_urls = ['https://f/login']
    urls = [
            'https://f/forums/140/',
            #'other urls'
            ]
    

#    rules = (
#        Rule(
#            LinkExtractor(
#                allow=('/?=page-\d+',),
#                ),
#            callback='parse_posts',
#            follow=True),
#        )


#    def get_next_page(self, response, func):
#        next_page = response.xpath('///a[@class="pageNav-jump pageNav-jump--next"]/@href').get()
#        if next_page is not None:
#            next_page = "https://" + self.allowed_domains[0].strip("[']") + next_page
#            print('next_page = [', next_page, ']\n')
#            return scrapy.Request(url=next_page, callback=func)
#        else:
#            raise Exception("Next page are over")



    def parse(self, response):

        logging.debug(f"\n\t\t[parse][PROCESSING]: [ {response.url} ]\n")

        token = response.css('form.block input::attr(value)').get()

        try:
            argv = self.argv.split()
            #atr = argv[::2]
            key = argv[1::2]
            login = key[0]
            password = key[1]
            url = key[2]
        
        except IndexError as err:
            logging.error(f'\n\t\t[parse]argv -> {err}\n')
            logging.error('\n\t\t[parse]argv -> Required argument missing\n')
            sys.exit(3)

#        if login is None or password is None or url is None:
#            logging.error('\n\t\tMissing arguments\n')
#            exit(4&)

        logging.debug(f"\n\t\ttoken = [' {token} ']\n")

        yield scrapy.FormRequest.from_response(
            response,
            url = "https://f/login/login",
            formdata={
                '_xfToken': token,
                'login': login,
                'password': password,
                },
            callback=self.after_login,
            meta={
                "url": url
                }
        )



    def after_login(self, response):

        # check login succeed before going on
#        if response.status == 403:
#           logging.debug("Login failed")
#           return
        
       # continue scraping with authenticated session...
        
        url = response.meta['url']

        try:
            yield scrapy.Request(url=url, callback=self.action)

        except ValueError as err:
            logging.debug(f"\n\t\t[after_login] -> {err}\n")
            #scrapy.crawler.stop()
            sys.exit(4)

        #yield scrapy.Request(self.urls[0], callback=self.get_link_last_page)



    def action(self, response):

        logging.debug(f"\n\t\t[action][PROCESSING]: [ {response.url} ]\n")
        
        all_threads = response.xpath('///div[@class="structItem-title"]')
        
        for thread in all_threads:
            link_part = thread.xpath('./a/@href[not(ancestor::a[@class="labelLink"])]').get().strip("unread")
            thread_link = "https://" + self.allowed_domains[0].strip("[']") + link_part

            last_msg_href = f'{link_part}latest'
            last_msg_time = parse(response.xpath('.//a[@href="' + last_msg_href + '"]/time/@datetime').get())
            last_msg_time = last_msg_time.replace(tzinfo=None)
 
            #print(f"\n\ntime={last_msg_time} ||| link={link_part}\n\n")

            time_last_msg_db = get_last_message(thread_link)
            if last_msg_time <= time_last_msg_db:
                 logging.info(f"[ Thread '{thread_link}' is completely in the database! ]\n")
                 continue

            logging.info(f"[ --> A new post was found in this thread : '{thread_link}' ]\n")
            yield scrapy.Request(thread_link, callback=self.get_link_last_page)


        threads_next_page = response.xpath('///a[@class="pageNav-jump pageNav-jump--next"]/@href').get()
        if threads_next_page is not None:
            logging.debug(f"\n\t\t[action]threads_next_page = [ {threads_next_page} ]\n")

            next_page_link = "https://" + self.allowed_domains[0].strip("[']") + threads_next_page
            
            yield scrapy.Request(url=next_page_link, callback=self.action)



    def get_link_last_page(self, response):

        logging.debug(f"\n\t\t[get_link_last_page][PROCESSING]: [ {response.url} ]\n")
        
        block_navi = response.xpath('.//div[@class="block-outer"]')
        link_last_page = block_navi.xpath('.//li[@class="pageNav-page "]/a/@href').get()

        if link_last_page is None:
            link_last_page = response.url
        else:
            link_last_page = "https://" + self.allowed_domains[0].strip("[']") + link_last_page
               
        return scrapy.Request(link_last_page, callback=self.get_messages, dont_filter=True, meta={'posts': None})



    def get_messages(self, response):

        logging.debug(f"\n\t\t[get_messages][PROCESSING]: [ {response.url} ]\n")

        time_last_msg_db = get_last_message(response.url)
        
        flag = False
        if response.meta['posts'] is not None:
            posts = response.meta['posts']
        else:
            posts = []

        content = response.xpath('///div[@class="message-main js-quickEditTarget"]')
        for p in content[::-1]:
            post_datetime = parse(p.xpath('.//time[@class="u-dt"]/@datetime').get())
            post_datetime = post_datetime.replace(tzinfo=None)
            
            #logging.debug(f"time=[ {time_last_msg_db} ]")
            if post_datetime <= time_last_msg_db:
                flag = True
                break
            
            post = PostItem()
            post['post_datetime'] = str(post_datetime)
            post['post_link'] = re.sub("page-\d+", "", response.url) + p.xpath('.//div/@data-lb-id').get()
            post['post_author'] = p.xpath('.//@data-lb-caption-desc').get().split(" · ")[0]
            
            #msg_link = p.xpath('.//article//a/@href').getall()
            #msg_file = p.xpath('.//section//a/@href').getall()
            msg_link = f"| .//article//a/@href | .//section//a/@href"
            message_list = p.xpath('.//article/descendant-or-self::text()' + msg_link).getall()

            post['post_message'] = list(filter(None, [i.strip(",\t\n ").strip(" , ") for i in message_list]))
            posts.append(post)
        
        
        earlier_page = response.xpath('.//a[@class="pageNav-jump pageNav-jump--prev"]/@href').get()
        if flag == False and earlier_page is not None:
            logging.debug(f"\n\t\t[get_messages]earlier_page = [ {earlier_page} ]\n")

            earlier_page_link = "https://" + self.allowed_domains[0].strip("[']") + earlier_page
            #request.meta['posts'] = posts

            yield scrapy.Request(
                    url=earlier_page_link,
                    callback=self.get_messages,
                    dont_filter=True,
                    meta={
                        "posts": posts
                        }
                    )
        else:
            header = response.xpath('.//div[@class="p-body-header"]')

            thread = ThreadItem()
            thread['thread_link'] = re.sub("page-\d+", "", response.url)
            thread['thread_name'] = header.xpath('./div[@class="p-title "]/h1[@class="p-title-value"]/text()').get()
            thread['thread_author'] = header.xpath('.//a[@class="username  u-concealed"]/descendant::text()').get()
            thread['create_date'] = header.xpath('.//div[2]/ul/li[2]/a/time/@datetime').get()

            yield {
                'thread': thread,           
                'posts' : posts
                }



'''

#            thread['thread_link'] = link_thread
#            thread['thread']['key']['thread_name'] = th.xpath('./div[@class="structItem-title"]/a/text()').get()
#            thread['thread']['key']['thread_author'] = th.xpath('.//a[@class="username "]/text()').get()
#            thread['thread']['key']['create_data'] = th.xpath('.//time[@class="u-dt"]/@datetime').get()
#            thread['thread']['key']['last_message'] = th.xpath('..//time[@class="structItem-latestDate u-dt"] \
#                                    /@datetime').get()

#            yield thread
            #yield scrapy.FormRequest.from_response(url=link_thread, callback=self.parse_posts)
'''
