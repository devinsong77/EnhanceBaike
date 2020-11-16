# -*- coding: utf-8 -*-
import urllib
import re
import pymongo
import scrapy
from scrapy.selector import Selector
import logging
import elasticsearch
from baike_spider.items import *


class BaikeSpider(scrapy.Spider):
    name = 'baike_spider'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['https://baike.baidu.com/item/清华大学']
    db = pymongo.MongoClient("mongodb://127.0.0.1:27017/")["db_kg"]
    baike_model = db['baike_model']
    db_triples = db['triples_model']
    olds = set([item['title'] for item in baike_model.find({}, {'title': 1})])

    # if len(olds) > 0:
    #     start_urls = ['https://baike.baidu.com/item/' + olds.pop()]

    def parse(self, response):
        page_url = response.request.url
        item_name = re.sub('/', '', re.sub('https://baike.baidu.com/item/',
                                           '', urllib.parse.unquote(response.url)))

        # 获取百科标题
        head_title = ''.join(response.xpath(
            '//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').getall()).replace('/', '')
        # 获取副标题
        sub_title = ''.join(response.xpath(
            '//dd[@class="lemmaWgt-lemmaTitle-title"]/h2/text()').getall()).replace('/', '')
        title = head_title + sub_title

        # 爬取过的直接忽视
        if title in self.olds:
            return

        # 将网页内容存入mongodb
        try:
            baike_item = BaikeItem()
            baike_item['baike_id'] = item_name
            baike_item['title'] = title
            baike_item['name'] = head_title
            baike_item['text'] = ''
            # 以段落为单位添加，并在段落结尾添加换行符
            for para in response.xpath('//div[@class="main-content"]/div[@class="para"] |//div[@class="main_tab main_tab-defaultTab  curTab"]/div[@class="para"] | //div[@class="lemma-summary"]/div[@class="para"]'):
                texts = para.xpath('.//text()').extract()
                for text in texts:
                    baike_item['text'] += text.strip('\n');
                baike_item['text'] += '<br/>'
            baike_item['page_url'] = page_url
            yield baike_item

        except pymongo.errors.DuplicateKeyError and elasticsearch.ConflictError:
            pass
        # 更新爬取过的item集合
        self.olds.add(title)
        # 爬取页面内的item
        items = set(response.xpath(
            '//a[contains(@href, "/item/")]/@href').re(r'/item/[A-Za-z0-9%\u4E00-\u9FA5]+'))
        for item in items:
            new_url = 'https://baike.baidu.com' + urllib.parse.unquote(item)
            new_item_name = re.sub(
                '/', '', re.sub('https://baike.baidu.com/item/', '', new_url))
            if new_item_name not in self.olds:
                yield response.follow(new_url, callback=self.parse)

        # 处理三元组
        entity = head_title
        attrs = response.xpath(
            '//dt[contains(@class,"basicInfo-item name")]').getall()
        values = response.xpath(
            '//dd[contains(@class,"basicInfo-item value")]').getall()
        if len(attrs) != len(values):
            return
        try:
            for attr, value in zip(attrs, values):
                # attr
                temp = Selector(text=attr).xpath(
                    '//dt//text()').getall()
                attr = ''.join(temp).replace('\xa0', '')
                # value
                value = ''.join(Selector(text=value).xpath(
                    '//dd/text()|//dd/a//text()').getall())
                try:
                    value = value.replace('\n', '')
                    logging.warning(title + ': ' + entity + '_' + attr + '_' + value)
                    triples_item = TriplesItem()
                    triples_item['triples_id'] = title
                    triples_item['item_name'] = entity
                    triples_item['attr'] = attr
                    triples_item['value'] = value
                    yield triples_item
                except pymongo.errors.DuplicateKeyError and elasticsearch.ConflictError:
                    pass
        except Exception:
            logging.error('\n---'.join(attrs) +
                          '\n_________________' + '\n---'.join(values))
