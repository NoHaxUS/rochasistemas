from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import CustomUser
from .models import Ticket,Cotation,Payment,Game,League,Reward,Location,Market
from user.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.main import ChangeList
import utils.timezone as tzlocal
from history.models import PunterPayedHistory
from django.contrib import messages
from admin_view_permission.admin import AdminViewPermissionModelAdmin
from .decorators import confirm_action
from django.utils.html import format_html


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


class HiddenGamesFilter(admin.SimpleListFilter):

    title = _('Visibilidade')
    parameter_name = 'visibility'

    def lookups(self, request, model_admin):
        return (
            ('list_all_hidden', _('Jogos Ocultos')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'list_all_hidden':
            return queryset.filter(is_visible=False)
        elif self.value() == None:
            return queryset.filter(is_visible=True)


class HiddenTicketFilter(admin.SimpleListFilter):

    title = _('Visibilidade')
    parameter_name = 'visibility'

    def lookups(self, request, model_admin):
        return (
            ('list_all_hidden', _('Tickets Ocultos')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'list_all_hidden':
            return queryset.filter(is_visible=False)
        elif self.value() == None:
            return queryset.filter(is_visible=True)


@confirm_action("Cancelar Ticket(s)")
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

    if request.user.has_perm('user.be_seller') and not request.user.is_superuser:
        if request.user.seller.can_cancel_ticket:
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


@confirm_action("Validar Ticket(s)")
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

@confirm_action("Pagar Apostador(es)")
def pay_winner_punter(modeladmin, request, queryset):

    if request.user.has_perm('user.be_seller'):
        for ticket in queryset:
            pay_winner_result = ticket.pay_winner_punter(request.user)
            if pay_winner_result['success']:
                messages.success(request, pay_winner_result['message'])
            else:
                messages.warning(request, pay_winner_result['message'])

pay_winner_punter.short_description = 'Pagar Apostador'


@confirm_action("Ocultar Ticket(s)")
def hide_ticket_action(modeladmin, request, queryset):

    if request.user.is_superuser:
        for ticket in queryset:
            result = ticket.hide_ticket()
            messages.success(request, result['message'])

hide_ticket_action.short_description = 'Ocultar Tickets'


@confirm_action("Ocultar Ticket(s)")
def show_ticket_action(modeladmin, request, queryset):

    if request.user.is_superuser:
        for ticket in queryset:
            result = ticket.show_ticket()
            messages.success(request, result['message'])

show_ticket_action.short_description = 'Exibir Tickets'


def payment_status(obj):
    if obj.payment:
        return ("%s" % obj.payment.status_payment)
payment_status.short_description = 'Status do Pagamento'


def bet_ticket_status(obj):
    if obj.bet_ticket_status == 'Venceu':
        return format_html (
            '<div class="winner_ticket">{}</div>',
            obj.bet_ticket_status
        )
    elif obj.bet_ticket_status == 'Não Venceu':
        return format_html (
            '<div class="loser_ticket">{}</div>',
            obj.bet_ticket_status
        )
    elif obj.bet_ticket_status == 'Cancelado':
        return format_html (
            '<div class="loser_ticket">{}</div>',
            obj.bet_ticket_status
        )

    return format_html (
            '<div class="">{}</div>',
            obj.bet_ticket_status
        )

bet_ticket_status.short_description = 'Status'

@admin.register(Ticket)
class BetTicketAdmin(AdminViewPermissionModelAdmin):
    search_fields = ['id']
    list_filter = ('bet_ticket_status',
    'payment__who_set_payment_id',
    'payment__status_payment',
    HiddenTicketFilter,
    'creation_date',
    'reward__status_reward')
    list_display =('pk', bet_ticket_status, 'get_ticket_link','get_punter_name','value','reward','cotation_sum', payment_status,'creation_date', 'seller_related')
    exclude = ('cotations','user','normal_user',)
    actions = [validate_selected_tickets, pay_winner_punter, cancel_ticket, hide_ticket_action, show_ticket_action]
    list_per_page = 50


    def has_add_permission(self, request):
        if request.user.is_superuser:
            return False
        return super().has_add_permission(request)


    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.is_superuser:
            valid_actions = ['cancel_ticket', 'hide_ticket_action','show_ticket_action']
            actions_copy = actions.copy()
            for action in actions_copy:
                if not action in valid_actions:
                    del actions[action]
            return actions

        if request.user.has_perm('user.be_seller'):
            valid_actions = ['validate_selected_tickets', 'pay_winner_punter', 'cancel_ticket']
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
            list_filter = list(super().get_list_filter(request))
            list_filter.remove('payment__who_set_payment_id')
            return list_filter

        if request.user.has_perm('user.be_manager'):
            return super().get_list_filter(request)

        

    def get_readonly_fields(self, request, obj):
        if request.user.has_perm('user.be_seller') and not request.user.is_superuser:
            return ('value','reward','payment','creation_date','cotation_sum', 'seller', 'bet_ticket_status','is_visible')
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        if request.user.has_perm('user.be_seller'):
            return qs.filter(Q(payment__status_payment=Payment.PAYMENT_STATUS[0][1],
            bet_ticket_status=Ticket.BET_TICKET_STATUS[0][1]) |
            Q(payment__who_set_payment=request.user.seller,
            is_visible=True))

        if request.user.has_perm('user.be_manager'):
            return qs.filter(payment__who_set_payment__my_manager=request.user.manager, is_visible=True)

        if request.user.has_perm('user.be_punter'):
            return qs.filter(user=request.user.punter, is_visible=True)
        



@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return False
        return super().has_delete_permission(request)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request):
        if request.user.is_superuser:
            return False
        return super().has_delete_permission(request)



@confirm_action("Ocultar Jogo(s)")
def hide_game_action(modeladmin, request, queryset):

    if request.user.is_superuser:
        for game in queryset:
            result = game.hide_game()
            messages.success(request, result['message'])

hide_game_action.short_description = 'Ocultar Jogos'


@confirm_action("Exibir Jogo(s)")
def show_game_action(modeladmin, request, queryset):

    if request.user.is_superuser:
        for game in queryset:
            result = game.show_game()
            messages.success(request, result['message'])

show_game_action.short_description = 'Exibir Jogos'

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_filter = (GamesWithNoFinalResults, HiddenGamesFilter)
    list_display = ('pk','name',)
    list_display_links = ('pk','name',)
    autocomplete_fields = ['league',]
    actions = [hide_game_action, show_game_action]
    list_per_page = 20


    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.is_superuser:
            valid_actions = ['hide_game_action','show_game_action']
            actions_copy = actions.copy()
            for action in actions_copy:
                if not action in valid_actions:
                    del actions[action]
            return actions

        if request.user.has_perm('user.be_seller'):
            return None
        
        if request.user.has_perm('user.be_manager'):
            return None

        if request.user.has_perm('user.be_punter'):
            return None



    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.has_perm('user.be_seller'):
            return qs
        if request.user.has_perm('user.be_manager'):
            return qs
        if request.user.has_perm('user.be_punter'):
            return qs
        



@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_display = ('pk','name',)
    list_display_links = ('pk','name')
    list_per_page = 20


    def has_delete_permission(self, request):
        if request.user.is_superuser:
            return False
        return super().has_delete_permission(request)
    


@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
    search_fields = ['id','name','game__name']
    autocomplete_fields = ['game','market',]
    list_display = ('pk','name', 'start_price', 'price', 'game', 'market')
    list_display_links = ('pk','name',)
    list_per_page = 20


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_display = ('pk','name', 'priority')
    list_display_links = ('pk','name')
    list_per_page = 20


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_display = ('pk','name','priority')
    list_display_links = ('pk','name')
    #autocomplete_fields = ['location',]
    list_per_page = 20

