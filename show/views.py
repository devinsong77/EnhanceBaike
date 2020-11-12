from LAC import LAC
from django.shortcuts import render
from django.views.generic.base import View, logger
# Create your views here.
from django.http import HttpResponse
import time
import redis

# redis连接
redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)
lac = LAC(mode='lac')


class IndexView(View):

    @staticmethod
    def get(request):
        # result = db_triples.objects.filter(_id="兴安县_地理位置_广西东北部")
        # logger.info(result[0].item_name)
        # scard集合内元素数量
        ser_list = []
        if redis_cli.scard('search_list') > 0:
            # logger.info("REDISSSSSSSSSSSSSSS")
            search_ser = redis_cli.smembers('search_list')
            for index, item in enumerate(list(search_ser)):
                if index >= 10:
                    break
                ser_list.append(item)
                logger.info(item)
        # ser_list 搜索历史数据传入前端展示
        return render(request, "index.html", {'search_list': ser_list})


class SearchView(View):
    my_labels = ['PER', 'LOC', 'ORG']

    def get(self, request):
        key_word = request.GET.get("wd", "")
        # SearchModel.objects.create(search_text=key_word)
        # start = time.clock()
        lac_result = lac.run(key_word)
        words = lac_result[0]
        labels = lac_result[1]
        for (word, label) in zip(words, labels):
            if label in self.my_labels:
                # 写入redis
                redis_cli.sadd('search_list', word)
        # logger.info("use time:%f", time.clock() - start)
        return render(request, "result.html")


class ResultView(View):

    def get(self, request):
        return HttpResponse()
