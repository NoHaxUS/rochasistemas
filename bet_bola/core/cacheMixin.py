from utils.cache import monster_cache_page

class CacheKeyDispatchMixin:
    def list(self, *args, **kwargs):
        return monster_cache_page(self.caching_time)(super().list)(*args, **kwargs)
        

class CacheKeyGetMixin:
    def get(self, *args, **kwargs):
        return monster_cache_page(self.caching_time)(self.get_logic)(*args, **kwargs)
