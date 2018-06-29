from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import CustomUser
from .models import BetTicket,Cotation,Payment,Game,Championship,Reward,Country,Market
from user.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.main import ChangeList
import utils.timezone as tzlocal
from history.models import PunterPayedHistory
from django.contrib import messages
from admin_view_permission.admin import AdminViewPermissionModelAdmin


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


def cancel_ticket(modeladmin, request, queryset):
    if request.user.is_superuser:
        for ticket in queryset:
            ticket_cancelation = ticket.cancel_ticket(request.user)
            if ticket_cancelation['success']:
                messages.success(request, ticket_cancelation['message'])
            else:
                messages.warning(request, ticket_cancelation['message'])
                break

    if request.user.has_perm('user.be_manager') and not request.user.is_superuser:
        if request.user.manager.can_cancel_ticket:
            for ticket in queryset:
                ticket_cancelation = ticket.cancel_ticket(request.user)
                if ticket_cancelation['success']:
                    messages.success(request, ticket_cancelation['message'])
                else:
                    messages.warning(request, ticket_cancelation['message'])
                    break
        else:
            messages.warning(request, "Você não tem permissão pra cancelar Tickets.")

cancel_ticket.short_description = 'Cancelar Ticket'

def validate_selected_tickets(modeladmin, request, queryset):
    
    if request.user.has_perm('user.be_seller'):
        for ticket in queryset:
            ticket_validation = ticket.validate_ticket(request.user)
            if ticket_validation['success']:
                from django.utils.safestring import mark_safe

                messages.success(request, mark_safe(ticket_validation['message']) )
            else:
                messages.warning(request, ticket_validation['message'])
                break

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




def payment_status(obj):
    if obj.payment:
        return ("%s" % obj.payment.status_payment)
payment_status.short_description = 'Status do Pagamento'


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(BetTicket)
class BetTicketAdmin(AdminViewPermissionModelAdmin):
    search_fields = ['id']
    list_filter = ('bet_ticket_status',
    'payment__who_set_payment_id',
    'payment__status_payment',
    'creation_date',
    'reward__status_reward')
    list_display =('pk','get_ticket_link','get_punter_name','value','reward','cotation_sum','bet_ticket_status', payment_status,'creation_date', 'seller_related')
    exclude = ('cotations','user','normal_user',)
    actions = [validate_selected_tickets, pay_winner_punter, cancel_ticket]
    list_per_page = 20


    def has_add_permission(self, request):
        if request.user.is_superuser:
            return False
        return super().has_add_permission(request)


    def get_actions(self, request):
        actions = super().get_actions(request)
        from collections import OrderedDict

        if request.user.is_superuser:
            valid_actions = ['cancel_ticket']
            actions_copy = actions.copy()
            for action in actions_copy:
                if not action in valid_actions:
                    del actions[action]
            return actions

        if request.user.has_perm('user.be_seller'):
            valid_actions = ['validate_selected_tickets', 'pay_winner_punter']
            actions_copy = actions.copy()
            for action in actions_copy:
                if not action in valid_actions:
                    del actions[action]
            return actions
        
        if request.user.has_perm('user.be_manager'):
            valid_actions = ['cancel_ticket']
            actions_copy = actions.copy()
            for action in actions_copy:
                if not action in valid_actions:
                    del actions[action]
            return actions

        if request.user.has_perm('user.be_punter'):
            return None


    def get_list_filter(self, request):

        if request.user.is_superuser:
            return super().get_list_filter(request)
            
        if request.user.has_perm('user.be_punter'):
            return None

        if request.user.has_perm('user.be_seller'):
            return ('bet_ticket_status','payment__status_payment',)

        if request.user.has_perm('user.be_manager'):
            return super().get_list_filter(request)

        

    def get_readonly_fields(self, request, obj):
        if request.user.has_perm('user.be_seller') and not request.user.is_superuser:
            return ('value','reward','payment','creation_date','cotation_value_total', 'seller', 'bet_ticket_status')
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.has_perm('user.be_seller'):
            return qs.filter(Q(payment__status_payment=Payment.PAYMENT_STATUS[0][1], 
            bet_ticket_status=BetTicket.BET_TICKET_STATUS[0][1]) | \
            Q(payment__status_payment=Payment.PAYMENT_STATUS[1][1],
            bet_ticket_status=BetTicket.BET_TICKET_STATUS[2][1], payment__who_set_payment=request.user.seller) | \
            Q(bet_ticket_status=BetTicket.BET_TICKET_STATUS[0][1], payment__status_payment=Payment.PAYMENT_STATUS[1][1], 
            payment__who_set_payment=request.user.seller ) )\
            .exclude(reward__status_reward=Reward.REWARD_STATUS[1][1])

        if request.user.has_perm('user.be_manager'):
            return qs.filter(payment__who_set_payment__my_manager=request.user.manager)

        if request.user.has_perm('user.be_punter'):
            return qs.filter(user=request.user.punter)
        


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_filter = (GamesWithNoFinalResults,)
    list_display = ('pk','name',)
    list_display_links = ('pk','name',)
    autocomplete_fields = ['championship',]
    list_per_page = 20


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_display = ('pk','name',)
    list_display_links = ('pk','name')
    list_per_page = 20


@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
    search_fields = ['id','name','game__name']
    autocomplete_fields = ['game','kind',]
    list_display = ('pk','name', 'original_value', 'value', 'game', 'kind')
    list_display_links = ('pk','name',)
    list_per_page = 20


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_display = ('pk','name', 'priority')
    list_display_links = ('pk','name')
    list_per_page = 20


@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_display = ('pk','name','country','priority')
    list_display_links = ('pk','name')
    autocomplete_fields = ['country',]
    list_per_page = 20

