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

class UtilsConfig(AppConfig):
    name = 'utils'
    verbose_name = 'Utilidades'

    def ready(self):
        post_migrate.connect(create_comission_to_existing_sellers, sender=self)