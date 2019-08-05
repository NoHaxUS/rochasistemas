from django.core.cache import cache

def invalidate_cache_group(cache_group):
    groups = cache.get('cache_groups')
    if groups:
        group = groups.get(cache_group)
        if group:
            cache.delete_many(group)
            return True
    return False
