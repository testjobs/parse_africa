import os
import logging

import scrapy
import PyPDF2
from pymongo import MongoClient
from africa.items import AfricaItem

logging.basicConfig(filename='logger.log', level=logging.INFO,
                    format=u'%(filename)s[LINE:%(lineno)d]# %(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

class AfricaSpyder(scrapy.Spider):
    name = 'africa'
    base_url = 'http://bioline.org.br'
    allowed_domains = ['bioline.org.br']
    start_urls = [
        'http://bioline.org.br/toc?id=md',
    ]
    full_text = ''
    item = {}

    def parse(self, response):
        logger.info('Start parsing')
        for link in response.css("th > a ::attr(href)").extract():
            next_page_journal = '{}{}'.format(self.base_url, link)
            if self.check_issue(next_page_journal):
                logger.info('This magazine already downloaded - {}'.format(next_page_journal))
                continue

            logger.info('This magazine is send to download - {}'.format(next_page_journal))
            yield scrapy.Request(response.urljoin(next_page_journal), callback=self.parse_journal_page)

    def parse_journal_page(self, response):
        for link in response.css("li > a ::attr(href)").extract():
            next_page_article = '{}{}'.format(self.base_url, link)
            logger.info('This article is send to download - {}'.format(next_page_article))
            yield scrapy.Request(response.urljoin(next_page_article), callback=self.parse_article_page)

    def parse_article_page(self, response):
        item = AfricaItem()
        item["Title"] = ''.join(response.xpath('//font[@class="AbstractTitle"]/text()').extract())
        item["Authors"] = ''.join(response.xpath('//font[@class="AbstractAuthor"]/text()').extract())
        # item["Authors Affiliations"] = response.css("li > a ::attr(href)").extract()
        item["Abstract"] = ''.join(response.xpath('//div[@class="AbstractText"]/text()').extract())
        item["Journal_name"] = ''.join(response.xpath('//font[@class="paperTitle"]/text()').extract())
        item["Journal_ISSN"] = ''.join(response.xpath('//font[@class="paperISSN"]/font[@class="paperISSN"]/text()').extract())

        full_text_page = '{}{}'.format(self.base_url, ''.join(response.xpath('//tr/td[@id="bottomLine"]/a/@href').extract()))
        request = scrapy.Request(response.urljoin(full_text_page), callback=self.save_pdf)
        request.meta['item'] = item

        yield request

    def save_pdf(self, response):
        item = response.meta['item']
        full_text = ''

        path = '{}{}'.format(response.url.split('/')[-1].replace('?', '_'), '.pdf')
        self.logger.info('Saving PDF %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)

        with open(path, 'rb') as pdf_file:
            read_pdf = PyPDF2.PdfFileReader(pdf_file)
            number_of_pages = read_pdf.getNumPages()
            for page in range(number_of_pages):
                full_text += read_pdf.getPage(page).extractText()
        os.remove(path)

        item["Full_text"] = full_text
        yield item

    def check_issue(self, link):
        client = MongoClient()
        db = client['magazines']
        collection = db['magazines_issues']
        if collection.find_one({'issue': link}) is None:
            collection.insert({'issue': link})
            return False
        return True