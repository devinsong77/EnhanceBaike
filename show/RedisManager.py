from django.conf import settings
import redis


class RedisManager:

    def __init__(self):
        self.redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # 获取集合长度
    def get_set_len(self, key):
        return self.redis_cli.scard(key)

    # 读取数据
    def read_from_set(self, key):
        return self.redis_cli.smembers(key)

    # 数据写入
    def write_to_set(self, key, value):
        self.redis_cli.sadd(key, value)
