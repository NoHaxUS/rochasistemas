from django.contrib import admin
from user.models import CustomUser
from core.models import BetTicket
from .models import Punter, Seller, Manager
from utils.models import GeneralConfigurations
from django.contrib import messages
from admin_view_permission.admin import AdminViewPermissionModelAdmin


admin.site.register(GeneralConfigurations)


@admin.register(Punter)
class PunterAdmin(admin.ModelAdmin):
    search_fields = ['first_name']
    list_display = ('pk','first_name')
    exclude = ('user_permissions','groups',)
    list_display_links = ('pk','first_name')



def pay_seller(modeladmin, request, queryset):
    who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.first_name

    for seller in queryset:
        seller.reset_revenue(who_reseted_revenue)
    
    messages.success(request, 'Vendedores Pagos')

pay_seller.short_description = 'Pagar Vendedores'

@admin.register(Seller)
class SellerAdmin(AdminViewPermissionModelAdmin):
    search_fields = ['id','first_name','username','email']
    filter_horizontal = ['user_permissions',]
    fields = ('username', 'first_name','last_name', 'password','email', 'cellphone', 'address', 'cpf', 'commission', 'credit_limit', 'my_manager', 'can_sell_unlimited', 'is_active')
    list_editable = ('credit_limit',)
    list_display = ('pk','username','full_name','actual_revenue','commission','net_value','out_money','credit_limit','can_sell_unlimited')
    list_display_links = ('pk','username',)
    autocomplete_fields = ['my_manager',]
    actions = [pay_seller]

    def get_actions(self, request):
        actions = super().get_actions(request)
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
                obj.is_staff = True
                obj.is_superuser = False

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



def pay_manager(modeladmin, request, queryset):
    who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.first_name

    for manager in queryset:
        manager.reset_revenue(who_reseted_revenue)
    
    messages.success(request, 'Gerentes Pagos')

pay_manager.short_description = 'Pagar Gerentes'

@admin.register(Manager)
class ManagerAdmin(AdminViewPermissionModelAdmin):
    search_fields = ['id','first_name','username','email']
    #filter_horizontal = ['user_permissions',]
    fields = ('username','password','first_name','last_name','email','cellphone','address','commission','credit_limit_to_add','is_staff')
    #fields = ('user_permissions','username','password','first_name','last_name','email','cellphone','address','commission','credit_limit_to_add','is_staff')
    list_display = ('pk','username','first_name','email','cellphone','actual_revenue','commission','net_value','out_money','credit_limit_to_add')
    list_editable = ('credit_limit_to_add',)
    list_display_links = ('pk','username',)
    actions = [pay_manager]

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


