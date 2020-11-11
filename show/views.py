from LAC import LAC
from django.shortcuts import render
from django.views.generic.base import View, logger
# Create your views here.
from django.http import HttpResponse
import time
import redis
# 通过redis与scrapy交互
from show.models import *

redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)
lac = LAC(mode='lac')

class IndexView(View):

    @staticmethod
    def get(request):
        # result = db_triples.objects.filter(_id="兴安县_地理位置_广西东北部")
        # logger.info(result[0].item_name)
        return render(request, "index.html")


class SearchView(View):

    my_labels = ['PER', 'LOC', 'ORG']

    def get(self, request):
        key_word = request.GET.get("wd", "")
        SearchModel.objects.create(search_text=key_word)
        start = time.clock()
        lac_result = lac.run(key_word)
        words = lac_result[0]
        labels = lac_result[1]
        for (word, label) in zip(words, labels):
            if label in self.my_labels:
                #写入redis
                redis_cli.lpush('scrapy_list', word)
        logger.info("use time:%f", time.clock() - start)
        return render(request, "result.html")


class ResultView(View):

    def get(self, request):
        return HttpResponse()
