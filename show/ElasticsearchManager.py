from elasticsearch import Elasticsearch


class ElasticsearchManager:

    def __init__(self):
        self.client = Elasticsearch(hosts=["127.0.0.1:9200"])

    def search(self, keyword, page):
        response = self.client.search(
            index="baike",
            request_timeout=60,
            body={
                "query": {
                    # constant_score精准匹配
                    "constant_score": {
                        "filter": {
                            "term": {
                                # "baike_id": keyword,
                                "baike_id": keyword,
                                # "fields": ["baike_id", "text"]
                            },
                            "term": {
                                "text": keyword,
                            },
                        },
                    }
                },
                "from": (page - 1) * 10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "baike_id": {},
                        "text": {},
                    }}})
        return response

    def get_hit_list(self, res):
        error_nums = 0
        hit_list = []
        for item in res['hits']['hits']:
            hit_dict = {}
            try:
                if "baike_id" in item["highlight"]:
                    hit_dict["baike_id"] = "".join(item["highlight"]["baike_id"])
                else:
                    hit_dict["baike_id"] = item["_source"]["baike_id"]
                if "text" in item["highlight"]:
                    hit_dict["text"] = "".join(
                        item["highlight"]["text"])
                else:
                    # 如果正文内没有高亮词，则显示前200个字符
                    hit_dict["text"] = item["_source"]["text"][:200]
                hit_dict["source_site"] = "百度百科"
                hit_list.append(hit_dict)
            except:
                error_nums = error_nums + 1
        return hit_list


if __name__ == '__main__':
    e = ElasticsearchManager()
    res = e.search("中国", 1)
    hi_list = e.get_hit_list(res)
    print(hi_list)
    print(res['hits']['total']['value'])
    # print(res)