from django.contrib import admin
from .models import Bet,BetTicket,Cotation,Payment,Game
# Register your models here.


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
	pass


@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):
	pass


@admin.register(Cotation)
class BetAdmin(admin.ModelAdmin):
	pass


@admin.register(Game)
class BetAdmin(admin.ModelAdmin):
	pass


@admin.register(Payment)
class BetAdmin(admin.ModelAdmin):
	pass