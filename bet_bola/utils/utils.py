def make_key(key, key_prefix, version):    
    string = ':'.join([key_prefix, str(version), key])
    print(key,"@@@",key_prefix)
    return string