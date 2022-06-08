# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
import time
import sys                                                                                          
import os  

PROJECT_PATH = os.environ.get('PROJECT_PATH')                                                       
sys.path.append(str(PROJECT_PATH))

from itemadapter import ItemAdapter                                                                                                    
from common_libs.database import push_thread_to_base, get_last_message


class DeepScrapyPipeline:

    def open_spider(self, spider):
        #self.file = open('%s.json' % time.strftime('%Y%m%d%H%M%S', time.localtime()), 'tw')
        #self.file = open('%s.json' % time.strftime('%Y.%m.%d-%H:%M:%S', time.localtime()), 'tw')
        #self.file = open('items.json', 'tw') #
        pass
    def close_spider(self, spider):
        #self.file.close()
        pass
    def process_item(self, item, spider):
        try:
            #line = json.dumps(ItemAdapter(item).asdict(), indent=4, ensure_ascii=False) + "\n"
            line = ItemAdapter(item).asdict()
            push_thread_to_base(line)
            #self.file.write(line)
        except Exception as e:
            print(e)
        return item
