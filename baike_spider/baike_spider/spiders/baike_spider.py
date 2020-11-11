# -*- coding: utf-8 -*-
import urllib
import re
import pymongo
from scrapy.selector import Selector
import logging
import elasticsearch
from baike_spider.items import *


class BaikeSpider(scrapy.Spider):
    name = 'baike_spider'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['https://baike.baidu.com/item/中国']
    db = pymongo.MongoClient("mongodb://127.0.0.1:27017/")["db_kg"]
    db_baike = db['db_baike']
    db_triples = db['triples_model']
    olds = set([item['baike_id'] for item in db_baike.find({}, {'baike_id': 1})])
    if len(olds) > 0:
        start_urls = ['https://baike.baidu.com/item/'+olds.pop()]

    def parse(self, response):
        item_name = re.sub('/', '', re.sub('https://baike.baidu.com/item/',
                                           '', urllib.parse.unquote(response.url)))
        # 爬取过的直接忽视
        if item_name in self.olds:
            return
        # 将网页内容存入mongodb
        try:
            baike_item = BaikeItem()
            baike_item['baike_id'] = item_name
            baike_item['text'] = ''.join(response.xpath('//div[@class="main-content"]').xpath('//div[@class="para"]//text()').getall())
            yield baike_item

        except pymongo.errors.DuplicateKeyError and elasticsearch.ConflictError:
            pass
        # 更新爬取过的item集合
        self.olds.add(item_name)
        # 爬取页面内的item
        items = set(response.xpath(
            '//a[contains(@href, "/item/")]/@href').re(r'/item/[A-Za-z0-9%\u4E00-\u9FA5]+'))
        for item in items:
            new_url = 'https://baike.baidu.com'+urllib.parse.unquote(item)
            new_item_name = re.sub(
                '/', '', re.sub('https://baike.baidu.com/item/', '', new_url))
            if new_item_name not in self.olds:
                yield response.follow(new_url, callback=self.parse)

        # 处理三元组
        entity = ''.join(response.xpath(
            '//h1/text()').getall()).replace('/', '')
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
                    logging.warning(entity+'_'+attr+'_'+value)
                    triples_item = TriplesItem()
                    triples_item['triples_id'] = entity+'_'+attr+'_'+value
                    triples_item['item_name'] = entity
                    triples_item['attr'] = attr
                    triples_item['value'] = value
                    yield triples_item
                except pymongo.errors.DuplicateKeyError and elasticsearch.ConflictError:
                    pass
        except Exception:
            logging.error('\n---'.join(attrs) +
                          '\n_________________'+'\n---'.join(values))
