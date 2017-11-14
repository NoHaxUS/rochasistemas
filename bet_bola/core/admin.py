from django.contrib import admin
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward
# Register your models here.


@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):
	exclude = ['reward','payment','value']
	search_fields = ['seller__first_name']
	list_filter = ('bet_ticket_status','punter','seller','payment__status_payment','reward__status_reward')
	

@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
	list_display = ['name']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	pass


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
	pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	pass

@admin.register(Reward)
class BetTicketAdmin(admin.ModelAdmin):
	pass
