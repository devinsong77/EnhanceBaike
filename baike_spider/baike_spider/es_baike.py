from elasticsearch_dsl import connections, Document, Keyword, Text, analyzer

connections.create_connection(hosts=["127.0.0.1:9200"])

my_analyzer = analyzer('ik_smart')


class BaikeIndex(Document):
    # keyword不进行分词，Text进行分词
    baike_id = Text(analyzer="ik_max_word")
    title = Keyword()
    text = Text(analyzer="ik_max_word")
    page_url = Keyword()
    class Index:
        name = 'baike'


class TriplesIndex(Document):
    triples_id = Text(analyzer="ik_max_word")
    item_name = Keyword()
    attr = Keyword()
    value = Keyword()

    class Index:
        name = 'triples'


if __name__ == "__main__":
    #初始化两个索引
    BaikeIndex.init()
    TriplesIndex.init()
