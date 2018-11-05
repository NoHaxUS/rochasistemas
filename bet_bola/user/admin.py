from django.contrib import admin
from user.models import CustomUser
from core.models import Ticket
from .models import Punter, Seller, Manager
from utils.models import GeneralConfigurations
from django.contrib import messages
from core.decorators import confirm_action


admin.site.register(GeneralConfigurations)


@admin.register(Punter)
class PunterAdmin(admin.ModelAdmin):
    search_fields = ['pk','first_name','username','cpf']
    list_display = ('username','first_name','cellphone')
    fields = ('username','password','first_name', 'last_name', 'cellphone', 'email','is_active')
    list_display_links = ('username',)
    list_per_page = 20


    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs
        if request.user.has_perm('user.be_manager'):
            return qs
        if request.user.has_perm('user.be_seller'):
            return qs
        if request.user.has_perm('user.be_punter'):
            return qs.filter(pk=request.user.pk)

    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser:
            return fields
        if request.user.has_perm('user.be_manager'):
            return ('username','password','first_name', 'last_name', 'cellphone', 'email','is_active')
        if request.user.has_perm('user.be_seller'):
            return ('username','password','first_name', 'last_name', 'cellphone', 'email','is_active')
        if request.user.has_perm('user.be_punter'):
            return ('username','password','first_name', 'last_name', 'cellphone', 'email')
    


@confirm_action("Pagar Cambista(s)")
def pay_seller(modeladmin, request, queryset):
    who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username

    for seller in queryset:
        seller.reset_revenue(who_reseted_revenue)
    
    messages.success(request, 'Cambistas Pagos')

pay_seller.short_description = 'Pagar Cambistas'

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    search_fields = ['pk','first_name','username','cpf']
    fields = ('username', 'first_name','last_name', 'password','email', 'cellphone', 'address', 'cpf', 'credit_limit', 'my_manager', 'can_sell_unlimited', 'is_active', 'can_cancel_ticket', 'limit_time_to_cancel')
    list_editable = ('credit_limit',)
    list_display = ('username','full_name','actual_revenue','out_money','net_value','real_net_value','credit_limit','see_comissions')
    list_display_links = ('username',)
    autocomplete_fields = ['my_manager',]
    actions = [pay_seller]
    list_per_page = 20

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            return actions
        if request.user.has_perm('user.be_manager'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.has_perm('user.be_manager'):
            return qs.filter(my_manager=request.user.manager)

        if request.user.has_perm('user.be_seller'):
            return qs.filter(pk=request.user.pk)
        

    def save_model(self, request, obj, form, change):
        if request.user.has_perm('user.be_manager') and not request.user.is_superuser:
            if form.is_valid():
                obj.can_sell_unlimited = False
                if obj.pk:
                    credit_transation = request.user.manager.manage_credit(obj)
                    if credit_transation['success']:
                        super().save_model(request, obj, form, change)
                        messages.success(request, credit_transation['message'])
                    else:
                        messages.warning(request, credit_transation['message'])
                else:
                    obj.my_manager = request.user.manager
                    credit_to_add = obj.credit_limit
                    obj.credit_limit = 0
                    super().save_model(request, obj, form, change)

                    obj.credit_limit = credit_to_add
                    credit_transation = request.user.manager.manage_credit(obj, is_new=True)                    
                    if credit_transation['success']:
                        messages.success(request, credit_transation['message'])
                    else:
                        messages.warning(request, credit_transation['message'])
         

        elif request.user.is_superuser:
            super().save_model(request, obj, form, change)


@confirm_action("Pagar Gerente(s)")
def pay_manager(modeladmin, request, queryset):
    who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username

    for manager in queryset:
        manager.reset_revenue(who_reseted_revenue)
    
    messages.success(request, 'Gerentes Pagos')

pay_manager.short_description = 'Pagar Gerentes'

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    search_fields = ['pk','first_name','username','cpf']
    fields = ('username','password','first_name','last_name','email','cellphone','cpf','address','commission','credit_limit_to_add','is_active','can_cancel_ticket','can_sell_unlimited')
    list_display = ('username','first_name','actual_revenue','get_commission','net_value','out_money','real_net_value','credit_limit_to_add')
    list_editable = ('credit_limit_to_add',)
    list_display_links = ('username',)
    actions = [pay_manager]
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.has_perm('user.be_manager'):
            return qs.filter(pk=request.user.pk)



    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            return actions


