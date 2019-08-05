from django.core.cache import cache

def invalidate_cache_group(cache_group, store_id):
    cache_time = 60 * 5
    store_id = str(store_id)

    groups = cache.get('cache_groups')
    if groups:
        store_group = groups.get(store_id)
        if store_group:
            group = store_group.get(cache_group)
            if group:
                cache.delete_many(group)
                del groups[store_id][cache_group]
                cache.set('cache_groups', groups, cache_time)
                
                print(cache.get('cache_groups'))

                return True
    return False
