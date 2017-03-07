# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# coding: utf8

import logging
from pymongo import MongoClient
from scrapy.conf import settings

logging.basicConfig(filename='logger.log', level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

# Data come here after parsing
class AfricaPipeline(object):
    def process_item(self, item, spider):
        connection = MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        collection = db[settings['MONGODB_COLLECTION']]
        collection.insert(item)
        logger.info('Article saved - {}'.format(item['Title']))
        return item

