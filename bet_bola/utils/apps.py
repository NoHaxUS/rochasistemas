from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_comission_to_existing_sellers(sender, **kwargs):
    from user.models import Seller
    from utils.models import  Comission

    updateBool = input("Create Comissions for Users? Say: y or n: ")
    if updateBool == "y":
        print("Creating Comission for Users")
        for seller in Seller.objects.all():
            comission = Comission.objects.filter(seller_related=seller)
            if not comission:
                Comission(seller_related=seller).save()

def create_default_priority(sender, **kwargs):
    from core.models import Country

    updateBool = input("Create default priority for countries? Say: y or n: ")
    if updateBool == "y":
        print("Setting Priorities")
        Country.objects.filter(pk=5).update(priority=100)
        Country.objects.filter(pk=11555657).update(priority=99)
        Country.objects.filter(pk=41).update(priority=98)
        Country.objects.filter(pk=32).update(priority=97)
        Country.objects.filter(pk=17).update(priority=95)


class UtilsConfig(AppConfig):
    name = 'utils'
    verbose_name = 'Utilidades'

    def ready(self):
        pass
        #post_migrate.connect(create_comission_to_existing_sellers, sender=self)
        #post_migrate.connect(create_default_priority, sender=self)
        