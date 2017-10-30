from django.contrib import admin
from .models import Bet
from .models import BetTicket
from .models import Cotation
from .models import Payment
# Register your models here.

admin.site.register(Bet)
admin.site.register(BetTicket)
admin.site.register(Cotation)
admin.site.register(Payment)