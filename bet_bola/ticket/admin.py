from django.contrib import admin
from ticket.models import Ticket, Reward, Payment
from django_admin_relation_links import AdminChangeLinksMixin

@admin.register(Ticket)
class TicketAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    autocomplete_fields = ('owner','creator')
    search_fields = ('ticket_id',)
    exclude = ['reward','payment','cotations',]
    #fields = ('ticket_id','owner')
    change_links = ['reward', 'payment']

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass