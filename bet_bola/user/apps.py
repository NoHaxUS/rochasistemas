from django.apps import AppConfig
from django.db.models.signals import post_migrate

def update_users_permissions_to_defaulf(sender, **kwargs):
    from user.models import Seller, Punter, Manager
    print("Updating Users Permissions")
    for seller in Seller.objects.all():
        #seller.is_staff = True
        seller.define_default_permissions()
        seller.save()
    """
    for manager in Manager.objects.all():
        manager.is_staff = True
        manager.define_default_permissions()
        manager.save()


    for punter in Punter.objects.all():
        punter.is_staff = True
        punter.define_default_permissions()
        punter.save()
    """


class UserConfig(AppConfig):
    name = 'user'
    verbose_name = "Usuários"
    
    def ready(self):
        #pass
        post_migrate.connect(update_users_permissions_to_defaulf, sender=self)

