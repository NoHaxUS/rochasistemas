from django.contrib import admin
from user.models import CustomUser
from .models import Ticket,Cotation,Payment,Game,League,Reward,Location,Market
from user.models import CustomUser
from django.contrib.auth.models import Group
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
import utils.timezone as tzlocal
from history.models import PunterPayedHistory
from django.contrib import messages
from .decorators import confirm_action
from django.utils.html import format_html


admin.site.unregister(Group)


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

def payment_status(obj):
    if obj.payment:
        return ("%s" % obj.payment.status_payment)
payment_status.short_description = 'Status do Pagamento'


def ticket_status(obj):
    if obj.ticket_status == Ticket.TICKET_STATUS['Venceu']:
        return format_html (
            '<div class="winner_ticket">{}</div>',
            obj.ticket_status
        )
    elif obj.ticket_status == Ticket.TICKET_STATUS['Não Venceu']:
        return format_html (
            '<div class="loser_ticket">{}</div>',
            obj.ticket_status
        )
    elif obj.ticket_status == Ticket.TICKET_STATUS['Cancelado']:
        return format_html (
            '<div class="canceled_ticket">{}</div>',
            obj.ticket_status
        )

    elif obj.ticket_status == Ticket.TICKET_STATUS['Venceu, não pago']:
        return format_html (
            '<div class="winner_not_paid">{}</div>',
            obj.ticket_status
        )

    return format_html (
            '<div class="wait_ticket">{}</div>',
            obj.ticket_status
        )

ticket_status.short_description = 'Status'

class TicketStatusListFilter(admin.SimpleListFilter):

    title = _('Ticket Status')
    parameter_name = 'ticket-status'


    def lookups(self, request, model_admin):
        return (
            ("Cancelado", "Cancelado"),
            ("Aguardando Resultados","Aguardando Resultados"),
            ("Não Venceu", "Não Venceu"),
            ("Venceu","Venceu"),
            ("Venceu, não pago","Venceu, não pago")
        )

    def queryset(self, request, queryset):

        if self.value() == "Cancelado":
            return queryset.filter(payment__status_payment="Cancelado")

        if self.value() == "Aguardando Resultados":
            return queryset\
            .annotate(cotations_num=Count('cotations__pk', filter=Q(cotations__status=1)))\
            .annotate(cotations_not_winner=Count('cotations__pk', filter=Q(cotations__settlement__in=[1,3,4])))\
            .filter(cotations_num__gt=0, cotations_not_winner=0).exclude(payment__status_payment='Cancelado')

        if self.value() == "Não Venceu":
            return queryset\
            .annotate(cotations_not_winner=Count('cotations__pk', filter=Q(cotations__settlement__in=[1,3,4])))\
            .filter(cotations_not_winner__gt=0)

        if self.value() == "Venceu":
            return queryset\
            .annotate(cotations_open=Count('cotations__pk', filter=Q(cotations__status=1)) )\
            .annotate(cotations_not_winner=Count('cotations__pk', filter=~Q(cotations__settlement__in=[2,5]) & ~Q(cotations__status=2) ) )\
            .filter(cotations_open=0, cotations_not_winner=0, payment__status_payment='Pago')

        if self.value() == "Venceu, não pago":
            return queryset\
            .annotate(cotations_open=Count('cotations__pk', filter=Q(cotations__status=1)) )\
            .annotate(cotations_not_winner=Count('cotations__pk', filter=~Q(cotations__settlement__in=[2,5]) & ~Q(cotations__status=2) ) )\
            .filter(cotations_open=0, cotations_not_winner=0).exclude(payment__status_payment='Pago')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_filter = (
    TicketStatusListFilter,
    'payment__who_set_payment_id',
    'payment__status_payment',
    'visible',
    'creation_date',
    'reward__reward_status')
    list_display = ('id', ticket_status, 
    'get_ticket_link',
    'get_punter_name',
    'value','reward',
    'cotation_sum', payment_status,'creation_date', 'seller_related')
    #exclude = ('cotations',)
    actions = [validate_selected_tickets, pay_winner_punter, cancel_ticket]
    list_per_page = 50




    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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


    def get_queryset(self, request):        
        qs = super().get_queryset(request)

        if request.user.is_superuser:            
            return qs
                
        if request.user.has_perm('user.be_seller'):            
            return qs.filter(payment__who_set_payment=request.user.seller,
            visible=True)

        if request.user.has_perm('user.be_manager'):
            return qs.filter(payment__who_set_payment__my_manager=request.user.manager, visible=True)

        if request.user.has_perm('user.be_punter'):
            return qs.filter(user=request.user.punter, visible=True)


    
        



#@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return False
        return super().has_delete_permission(request)

#@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request):
        if request.user.is_superuser:
            return False
        return super().has_delete_permission(request)
    

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_filter = ('visible', )
    list_display = ('id','name', 'visible')
    list_editable = ('visible',)
    list_display_links = ('id','name',)
    autocomplete_fields = ['league',]
    list_per_page = 20



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
    list_display = ('id','name',)
    list_filter = ('available',)
    #list_editable = ('available',)
    list_display_links = ('id','name')
    list_per_page = 40

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    


@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
    search_fields = ['id','name','game__name']
    autocomplete_fields = ['game',]
    list_filter = ('market',)
    list_display = ('id','name', 'start_price', 'price', 'game', 'market')
    list_display_links = ('id','name',)
    exclude = ('is_updating',)
    list_per_page = 20



@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    list_filter = ('visible',)
    list_display = ('id','name', 'priority','visible')
    list_editable = ('priority','visible')
    list_display_links = ('id','name')
    list_per_page = 20


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    search_fields = ['id','name','location__name']
    list_filter = ('visible',)
    list_display = ('id','name','location','priority', 'visible')
    list_display_links = ('id','name')
    autocomplete_fields = ['location',]
    list_editable = ('priority','visible')
    list_per_page = 20

