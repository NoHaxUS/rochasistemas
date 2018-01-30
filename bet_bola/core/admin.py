from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward
from user.models import CustomUser
from django.contrib.auth.models import Group
# Register your models here.



admin.site.unregister(Group)


@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):	
	search_fields = ['user__first_name']
	search_fields_hint = 'Buscar pelo nome do Vendedor'
	list_filter = ('bet_ticket_status','payment__who_set_payment_id','payment__status_payment','reward__status_reward')
	list_display =('pk','user','creation_date','reward','value','cota_total','bet_ticket_status')
	

@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
	search_fields = ['game_id__name']
	list_display = ('pk','game','original_value','value')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	search_fields = ['name']
	search_fields_hint = 'Buscar pelo nome do Jogo'


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
	search_fields = ['name']
	search_fields_hint = 'Buscar pelo nome do Campeoanto'


