from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import CustomUser
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward,Country
from user.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
# Register your models here.



class GamesWithNoFinalResults(admin.SimpleListFilter):

	title = _('Jogos sem resultado final')
	parameter_name = 'games_with_no_final_results'

	def lookups(self, request, model_admin):
		return (
			('list_all', _('Jogos sem resultado final')),
		)

	def queryset(self, request, queryset):
		if self.value() == 'list_all':
			return queryset.filter(status_game='FT', ft_score__isnull=True)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
	pass



@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):	
	search_fields = ['user__first_name']
	list_filter = ('bet_ticket_status',
	'payment__who_set_payment_id',
	'payment__status_payment',
	'reward__status_reward')
	list_display =('pk','user','creation_date','reward','value','cotation_sum','bet_ticket_status')
	exclude = ('cotations',)
	autocomplete_fields = ('user',)



@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
	search_fields = ['game_id__name']
	list_display = ('pk','game','original_value','value')
	fieldsets = (
		(None, {
			'fields': ('name','original_value', 'value','game','is_standard','total')
		}),
	)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	search_fields = ['name']
	list_filter = (GamesWithNoFinalResults,)
	fieldsets = (
		(None, {
			'fields': ('name','ht_score','ft_score','status_game')
		}),
	)
	list_display = ('name',)
	search_fields_hint = 'Buscar pelo nome do Jogo'


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
	search_fields = ['name']
	search_fields_hint = 'Buscar pelo nome do Campeoanto'


