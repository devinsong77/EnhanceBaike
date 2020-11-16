from elasticsearch import Elasticsearch


class ElasticsearchManager:

    def __init__(self):
        self.client = Elasticsearch(hosts=["127.0.0.1:9200"])

    # elasticsearch数据库搜索
    def search(self, keyword, page, type):
        switch = {
            "all": 'all',
            "per": '人物',
            "loc": '地点',
            "org": '组织',
        }
        type = switch[type]
        if type == 'all':
            # 类别为all是无需限制type
            response = self.client.search(
                index="baike",
                request_timeout=60,
                body={
                    "query": {
                        "bool": {
                            "should": [
                                {"match_phrase": {"text": keyword}},
                                {"term": {"name": keyword}},
                            ]
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "name": {},
                            "text": {},
                        }}})
        else:
            response = self.client.search(
                index="baike",
                request_timeout=60,
                # elasticsearch复合查询
                # 相当于 ((type== type) and (keyword in text) or (keyword in name))
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "bool": {
                                        "must": {
                                            "term": {
                                                "type": type
                                            }
                                        }
                                    }
                                },
                                {
                                    "bool": {
                                        "should": [
                                            {
                                                "match_phrase": {
                                                    "text": keyword
                                                }
                                            },
                                            {
                                                "term": {
                                                    "name": keyword
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                    ,
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "name": {},
                            "text": {},
                        }}})
        return response

    # 调整搜索数据格式
    def get_hit_list(self, res, keyword):
        error_nums = 0
        hit_list = []
        for item in res['hits']['hits']:
            hit_dict = {}
            try:
                hit_dict["baike_id"] = item["_source"]["title"]
                hit_dict["name"] = item["_source"]["name"]

                if "text" in item["highlight"]:
                    hit_dict["text"] = "".join(
                        item["highlight"]["text"][:200])
                else:
                    # 如果正文内没有高亮词，则显示前200个字符
                    hit_dict["text"] = item["_source"]["text"][:200]
                # 返回dict添加属性
                hit_dict["source_site"] = item["_source"]["type"]
                hit_dict["url"] = item["_source"]["page_url"]
                hit_dict["title"] = item["_source"]["title"]
                if hit_dict["name"] == keyword:
                    hit_list.insert(0, hit_dict)
                else:
                    hit_list.append(hit_dict)
            except:
                error_nums = error_nums + 1
        return hit_list


if __name__ == '__main__':
    e = ElasticsearchManager()
    res = e.search("中国科学技术大学", 1, "per")

    # 这里要加一个判断逻辑，判断是否有直接的搜索
    hi_list = e.get_hit_list(res, "中国科学技术大学")
    print("res ***********************")
    print(res)
    print(res['hits'])
    print(len(hi_list))
    print(res['hits']['total']['value'])
    # print(res)
