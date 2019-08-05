from django.utils.cache import get_cache_key
from django.core.cache import cache
from rest_framework.response import Response
from django.views.decorators.cache import cache_page

class CacheKeyDispatchMixin:
    def dispatch(self, *args, **kwargs):
        cache_key = get_cache_key(self.request)
        self.get_or_store_cache_key(cache_key, self.cache_group)
        return cache_page(self.caching_time)(super().dispatch)(*args, **kwargs)
        
        
    def get_or_store_cache_key(self, cache_key, cache_group):
        groups = cache.get('cache_groups')
        if not groups:
            groups = {}
            groups[cache_group] = []
            if cache_key:
                groups[cache_group].append(cache_key)
                cache.set('cache_groups', groups, self.caching_time)
        elif not groups.get(cache_group):
            groups[cache_group] = []
            if cache_key:
                groups[cache_group].append(cache_key)
                cache.set('cache_groups', groups, self.caching_time)
        else:
            if cache_key not in groups[cache_group]:
                if cache_key:
                    groups[cache_group].append(cache_key)
                    cache.set('cache_groups', groups, self.caching_time)
        
        print(groups)


class CacheKeyGetMixin:
    def get(self, *args, **kwargs):
        cache_key = get_cache_key(self.request)
        self.get_or_store_cache_key(cache_key, self.cache_group)
        return cache_page(self.caching_time)(super().get)(*args, **kwargs)
        
        
    def get_or_store_cache_key(self, cache_key, cache_group):
        groups = cache.get('cache_groups')
        if not groups:
            groups = {}
            groups[cache_group] = []
            if cache_key:
                groups[cache_group].append(cache_key)
                cache.set('cache_groups', groups, self.caching_time)
        elif not groups.get(cache_group):
            groups[cache_group] = []
            if cache_key:
                groups[cache_group].append(cache_key)
                cache.set('cache_groups', groups, self.caching_time)
        else:
            if cache_key not in groups[cache_group]:
                if cache_key:
                    groups[cache_group].append(cache_key)
                    cache.set('cache_groups', groups, self.caching_time)
        
        print(groups)