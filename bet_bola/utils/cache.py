from django.core.cache import cache
from django.middleware.cache import CacheMiddleware
from django.utils.decorators import decorator_from_middleware_with_args
from collections import defaultdict
from django.utils.cache import (
    get_cache_key, get_max_age, has_vary_header, learn_cache_key,
    patch_response_headers,
)


def invalidate_cache_group(cache_groups, store_id):
    cache_time = 60 * 5
    store_id = str(store_id)

    cache_set = cache.get('cache_set')
    if cache_set:
        for cache_group in cache_groups:
            store_group = cache_set.get(store_id)
            if store_group:
                group = store_group.get(cache_group)
                if group:
                    cache.delete_many(group)
                    del cache_set[store_id][cache_group]
                    cache.set('cache_set', cache_set, cache_time)


def get_or_store_cache_key(request, cache_key, cache_group):
    store_id = str(request.GET.get('store')) or str(request.user.my_store.pk)
    cache_time = 60 * 5

    if not store_id:
        raise ValueError("Failed to get store_id on cache definition")
        
    cache_set = cache.get('cache_set')

    if not cache_set:
        cache_set = defaultdict(dict)
        cache_set[store_id][cache_group] = []
        if cache_key:
            cache_set[store_id][cache_group].append(cache_key)
            cache.set('cache_set', cache_set, cache_time)
    elif not cache_set[store_id].get(cache_group):
        cache_set[store_id][cache_group] = []
        if cache_key:
            cache_set[store_id][cache_group].append(cache_key)
            cache.set('cache_set', cache_set, cache_time)
    else:
        if cache_key not in cache_set[store_id][cache_group]:
            if cache_key:
                cache_set[store_id][cache_group].append(cache_key)
                cache.set('cache_set', cache_set, cache_time)


class MonsterCacheMiddleware(CacheMiddleware):
    def process_response(self, request, response):
        """Set the cache, if needed."""
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.
            return response

        if response.streaming or response.status_code not in (200, 304):
            return response

        # Don't cache responses that set a user-specific (and maybe security
        # sensitive) cookie in response to a cookie-less request.
        if not request.COOKIES and response.cookies and has_vary_header(response, 'Cookie'):
            return response

        # Don't cache a response with 'Cache-Control: private'
        if 'private' in response.get('Cache-Control', ()):
            return response

        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout is None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        patch_response_headers(response, timeout)
        if timeout and response.status_code == 200:
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix, cache=self.cache)
            get_or_store_cache_key(request, cache_key, request.path)
            if hasattr(response, 'render') and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response, timeout)
        return response


def monster_cache_page(timeout, *, cache=None, key_prefix=None):
    return decorator_from_middleware_with_args(MonsterCacheMiddleware)(
        cache_timeout=timeout, cache_alias=cache, key_prefix=key_prefix
    )