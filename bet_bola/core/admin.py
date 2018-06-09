from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import CustomUser
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward,Country
from user.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.main import ChangeList
import utils.timezone as tzlocal
from history.models import PunterPayedHistory
from django.contrib import messages


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


def validate_selected_tickets(modeladmin, request, queryset):
    
    if request.user.has_perm('user.be_seller'):
        validate_all = True
        validated_ticket = []
        for ticket in queryset:
            if not ticket.validate_ticket(request.user):
                validate_all = False
                break
            validated_ticket.append(str(ticket.pk))
        if not validate_all:
            messages.success(request, 'Tickets' + ','.join(validated_ticket)+ 'validados, porém o saldo não foi suficiente para validar todos os selecionados.')
        else:
            messages.success(request, 'Todos os tickets foram validados.')

    
validate_selected_tickets.short_description = 'Validar Tickets'


def pay_winner_punter(modeladmin, request, queryset):

    if request.user.has_perm('user.be_seller'):
        for ticket in queryset:
            pay_winner_result = ticket.pay_winner_punter(request.user)
            if pay_winner_result['success']:
                messages.success(request, pay_winner_result['message'])
            else:
                messages.warning(request, pay_winner_result['message'])


pay_winner_punter.short_description = 'Pagar Apostador'





@admin.register(BetTicket)
class BetTicketAdmin(admin.ModelAdmin):	
    search_fields = ['user__first_name']
    list_filter = ('bet_ticket_status',
    'payment__who_set_payment_id',
    'payment__status_payment',
    'creation_date',
    'payment__seller_was_rewarded',
    'reward__status_reward')
    list_display =('pk','creation_date','value','reward','cotation_sum','bet_ticket_status')
    exclude = ('cotations','user','normal_user',)
    actions = [validate_selected_tickets, pay_winner_punter]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(payment__status_payment='Aguardando Pagamento do Ticket')
        #return qs

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = (GamesWithNoFinalResults,)
    fields = ('name','ht_score','ft_score','status_game','odds_processed','championship')
    list_display = ('pk','name',)
    list_display_links = ('pk','name',)

