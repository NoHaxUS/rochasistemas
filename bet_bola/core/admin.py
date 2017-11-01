from django.contrib import admin
from .models import Bet,Payment,BetTicket,Cotation,Game
# Register your models here.

admin.site.register(Bet)
admin.site.register(BetTicket)
admin.site.register(Cotation)
admin.site.register(Payment)
admin.site.register(Game)