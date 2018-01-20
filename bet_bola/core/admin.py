from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward
from user.models import CustomUser
# Register your models here.



admin.site.register(CustomUser, UserAdmin)

@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):	
	search_fields = ['user__first_name']
	list_filter = ('bet_ticket_status','payment__who_set_payment_id','payment__status_payment','reward__status_reward')
	list_display =('pk','user','creation_date','reward','value','bet_ticket_status', 'cota_total')
	

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
