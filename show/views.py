from LAC import LAC
from django.shortcuts import render
from django.views.generic.base import View, logger
# Create your views here.
from django.http import HttpResponse
from datetime import datetime
import redis

# redis连接
from show.ElasticsearchManager import ElasticsearchManager

redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)
lac = LAC(mode='lac')


class IndexView(View):

    @staticmethod
    def get(request):
        # scard集合内元素数量
        ser_list = []
        if redis_cli.scard('search_list') > 0:
            # logger.info("REDISSSSSSSSSSSSSSS")
            search_ser = redis_cli.smembers('search_list')
            for index, item in enumerate(list(search_ser)):
                if index >= 10:
                    break
                ser_list.append(item)
        # ser_list 搜索历史数据传入前端展示
        return render(request, "index.html", {'search_list': ser_list})


class SearchView(View):
    my_labels = ['PER', 'LOC', 'ORG']
    my_eManager = ElasticsearchManager()

    def get(self, request):
        key_word = request.GET.get("wd", "")
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except BaseException:
            page = 1

        lac_result = lac.run(key_word)
        words = lac_result[0]
        labels = lac_result[1]

        for (word, label) in zip(words, labels):
            if label in self.my_labels:
                # 写入redis
                redis_cli.sadd('search_list', word)

        # logger.info("use time:%f", time.clock() - start)
        start_time = datetime.now()
        res = self.my_eManager.search(key_word, page)
        hit_list = self.my_eManager.get_hit_list(res)
        end_time = datetime.now()
        total_nums = int(res["hits"]["total"]["value"])
        last_seconds = (end_time - start_time).total_seconds()
        # 计算出总页数
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)
        return render(request, "result.html", {"page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_word,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "s_type": "baike",
                                               })


class DetailView(View):

    def get(self, request):
        ###
        a = 1
        return HttpResponse()
