# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# Fields which will save in db
class AfricaItem(scrapy.Item):
    _id = scrapy.Field()
    Title = scrapy.Field()
    Authors = scrapy.Field()
    # Authors Affiliations
    Abstract = scrapy.Field()
    Full_text = scrapy.Field()
    Journal_name = scrapy.Field()
    Journal_ISSN = scrapy.Field()