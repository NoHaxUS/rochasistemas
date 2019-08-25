from utils.cache import monster_cache_page
from django.core.cache import cache

class CacheKeyDispatchMixin:
    def list(self, *args, **kwargs):
        # print('==== CACHE START =====')
        # cache_set = cache.get('cache_set')
        # print(cache_set)
        # ('===== CACHE END =====')
        return monster_cache_page(self.caching_time)(super().list)(*args, **kwargs)
        

class CacheKeyGetMixin:
    def get(self, *args, **kwargs):
        return monster_cache_page(self.caching_time)(self.get_logic)(*args, **kwargs)
