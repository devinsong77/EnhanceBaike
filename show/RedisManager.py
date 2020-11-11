from django.conf import settings
from django.core.cache import cache


class RedisManager:

    def __init__(self, key):
        self.key = key

    def read_from_cache(self):
        value = cache.get(self.key)
        return value

    def write_to_cache(self, value):
        cache.set(self.key, value, settings.CUBES_REDIS_TIMEOUT)
