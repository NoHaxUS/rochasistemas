def make_key(key, key_prefix, version):
    from django.core.cache import cache
    string = ':'.join([key_prefix, str(version), key])
    #print(cache.get('test', {}, 100))
    print(key)
    return string
