from django.utils.cache import get_cache_key
from django.core.cache import cache
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from collections import defaultdict


def get_or_store_cache_key(request, cache_key, cache_group):
    store_id = request.GET.get('store') or request.user.my_store.pk
    store_id = str(store_id)
    cache_time = 60 * 5

    if not store_id:
        raise ValueError("Failed to get store_id")
        
    groups = cache.get('cache_groups')

    if not groups:
        groups = defaultdict(dict)
        groups[store_id][cache_group] = []
        if cache_key:
            groups[store_id][cache_group].append(cache_key)
            cache.set('cache_groups', groups, cache_time)
    elif not groups.get(cache_group):
        groups[store_id][cache_group] = []
        if cache_key:
            groups[store_id][cache_group].append(cache_key)
            cache.set('cache_groups', groups, cache_time)
    else:
        if cache_key not in groups[store_id][cache_group]:
            if cache_key:
                groups[store_id][cache_group].append(cache_key)
                cache.set('cache_groups', groups, cache_time)
    
    print(groups)


class CacheKeyDispatchMixin:
    def list(self, *args, **kwargs):
        cache_key = get_cache_key(self.request)
        get_or_store_cache_key(self.request, cache_key, self.cache_group)
        return cache_page(self.caching_time)(super().list)(*args, **kwargs)
        

class CacheKeyGetMixin:
    def get(self, *args, **kwargs):
        cache_key = get_cache_key(self.request)
        get_or_store_cache_key(self.request, cache_key, self.cache_group)
        return cache_page(self.caching_time)(super().get)(*args, **kwargs)
