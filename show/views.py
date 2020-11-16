from django.shortcuts import render
from django.views.generic.base import View, logger
from datetime import datetime
from show.RedisManager import RedisManager

# redis连接
from show.ElasticsearchManager import ElasticsearchManager


class IndexView(View):
    # redis管理类对象
    rm = RedisManager()

    def get(self, request):
        # scard集合内元素数量
        ser_list = []
        if self.rm.get_set_len('search_list') > 0:
            search_ser = self.rm.read_from_set('search_list')
            for index, item in enumerate(list(search_ser)):
                if index >= 10:
                    break
                ser_list.append(item)
        # ser_list 搜索历史数据传入前端展示
        return render(request, "index.html", {'search_list': ser_list})


class SearchView(View):
    # elasticsearch管理类对象
    my_eManager = ElasticsearchManager()
    # redis管理类对象
    rm = RedisManager()

    def get(self, request):
        # get方法获取url参数
        b_type = request.GET.get("type", "all")
        key_word = request.GET.get("wd", "")
        page = request.GET.get("p", "1")

        try:
            page = int(page)
        except BaseException:
            page = 1

        # 写入redis
        self.rm.write_to_set('search_list', key_word)

        start_time = datetime.now()
        # elasticsearch搜索
        res = self.my_eManager.search(key_word, page, b_type)
        # 搜索结果调整
        hit_list = self.my_eManager.get_hit_list(res, key_word)
        end_time = datetime.now()
        # 计算结果总数
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
                                               "pre_type": b_type,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "s_type": "baike",
                                               })
