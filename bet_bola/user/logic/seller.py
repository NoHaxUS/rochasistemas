def define_default_permissions(self):        
    from django.contrib.auth.models import Permission
    be_seller_perm = Permission.objects.get(codename='be_seller')
    self.user_permissions.add(be_seller_perm)