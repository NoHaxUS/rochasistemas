from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_comission_to_existing_sellers(sender, **kwargs):
    from user.models import Seller
    from utils.models import  SellerComission

    updateBool = input("Create Comissions for Users? Say: y or n: ")
    if updateBool == "y":
        print("Creating Comission for Users")
        for seller in Seller.objects.all():
            comission = SellerComission.objects.filter(seller_related=seller)
            if not comission:
                SellerComission(seller_related=seller).save()

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

def correct_cancelled_tickets(sender, **kwargs):
    from core.models import Ticket

    print("Correcting cancelled Tickets.")
    cancelled_tickets = Ticket.objects.filter(ticket_status = Ticket.TICKET_STATUS[4][1])

    for ticket in cancelled_tickets:
        # ticket.payment.seller_was_rewarded = True
        ticket.payment.save()
        

class UtilsConfig(AppConfig):
    name = 'utils'
    verbose_name = 'Utilidades'

    def ready(self):
        pass
        #post_migrate.connect(correct_cancelled_tickets, sender=self)
        #post_migrate.connect(create_comission_to_existing_sellers, sender=self)
        #post_migrate.connect(create_default_priority, sender=self)
        