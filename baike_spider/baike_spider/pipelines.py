# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

from baike_spider.es_baike import TriplesIndex, BaikeIndex
from baike_spider.items import BaikeItem
from baike_spider.items import TriplesItem
from elasticsearch_dsl import connections, analyzer


class BaikePipeline(object):
    def __init__(self):

        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['db_kg']
        self.baike = self.db['baike_model']
        self.triples = self.db['triples_model']
        self.connections = connections.create_connection(hosts=["127.0.0.1:9200"])
        self.my_analyzer = analyzer('ik_smart')

    def process_item(self, item, spider):
        # 通过isinstance来区分item
        if isinstance(item, BaikeItem):
            # baike存入elasticsearch
            baike_index = BaikeIndex()
            baike_index.baike_id = item['baike_id']
            baike_index.title = item['title']
            baike_index.name = item['name']
            baike_index.text = item['text']
            baike_index.page_url = item['page_url']
            baike_index.save()
            # baike存入mongodb
            self.baike.insert_one(
                {
                    'baike_id': item['baike_id'],
                    'title': item['title'],
                    'name': item['name'],
                    'text': item['text'],
                    'page_url': item['page_url'],
                })

        # triples可能不需要索引
        if isinstance(item, TriplesItem):
            # triples存入elasticsearch
            triples_index = TriplesIndex()
            triples_index.triples_id = item['triples_id']
            triples_index.item_name = item['item_name']
            triples_index.attr = item['attr']
            triples_index.value = item['value']
            triples_index.save()
            # triples存入mongodb
            self.triples.insert_one({
                "triples_id": item['triples_id'],
                "item_name": item['item_name'],
                "attr": item['attr'],
                "value": item['value'],
            })
