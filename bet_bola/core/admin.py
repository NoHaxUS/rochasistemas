from django.contrib import admin
from .models import Bet,BetTicket,Cotation,Payment,Game,Championship
# Register your models here.


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
	pass


@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):
	pass


@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
	pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	pass


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
	pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	pass

