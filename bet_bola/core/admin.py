from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import CustomUser
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward,Country
from user.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.main import ChangeList


admin.site.unregister(Group)

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


@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):	
	search_fields = ['user__first_name']
	list_filter = ('bet_ticket_status',
	'payment__who_set_payment_id',
	'payment__status_payment',
	'creation_date',
	'payment__seller_was_rewarded',
	'reward__status_reward')
	list_display =('pk','real_punter_name','creation_date','value','reward','cotation_sum','bet_ticket_status')
	exclude = ('cotations','user','normal_user',)


"""
	def get_total_bet_reward(self, request):
		cl = self.get_changelist(request)
		qs = cl.get_queryset()
		total_bet = 0
		total_reward = 0
		for ticket in qs:
			total_bet += ticket.value
			total_reward+= ticket.reward.value
		
		self.total_bet = total_bet
		self.total_reward = total_reward
		return total_bet, total_reward

"""
"""
	def changelist_view(self, request, extra_context=None):
		extra_context = extra_context or {}
		extra_context['a'], extra_context['b'] = self.get_total_bet_reward(request)
		return super().changelist_view(request, extra_context)

"""

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	search_fields = ['name']
	list_filter = (GamesWithNoFinalResults,)
	fields = ('name','ht_score','ft_score','status_game',)
	list_display = ('pk','name',)
	list_display_links = ('pk','name',)


