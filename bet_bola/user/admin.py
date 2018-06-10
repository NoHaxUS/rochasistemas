from django.contrib import admin
from guardian.admin import GuardedModelAdmin
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
    fields = ('user_permissions','is_staff','username', 'first_name','last_name', 'password','email', 'cellphone', 'address', 'cpf', 'commission', 'credit_limit', 'my_manager', 'can_sell_unlimited', 'is_active')
    list_editable = ('credit_limit',)
    list_display = ('pk','username','full_name','actual_revenue','net_value','commission','credit_limit', 'can_sell_unlimited')
    list_display_links = ('pk','username',)
    actions = [pay_seller]

    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(my_manager=request.user.manager)

    def save_model(self, request, obj, form, change):
        from pprint import pprint
      
        obj.is_superuser = False
        if request.user.has_perm('user.be_manager') and not request.user.is_superuser:
            if form.is_valid():
                if obj.my_manager:
                    if obj.my_manager.pk == request.user.pk:
                        seller = Seller.objects.get(pk=obj.pk)
                        manager = obj.my_manager

                        diff = obj.credit_limit - seller.credit_limit
                        manager_balance_after = manager.credit_limit_to_add - diff

                        obj.can_sell_unlimited = seller.can_sell_unlimited

                        if manager_balance_after < 0:
                            messages.warning(request, 'Você não tem saldo suficiente.')
                            obj.status = 'NO'
                        elif obj.credit_limit < 0:
                            messages.warning(request, 'O saldo mínimo é 0.')
                            obj.status = 'NO'
                        else:
                            manager.credit_limit_to_add -= diff
                            manager.save()
                            super().save_model(request, obj, form, change)
                        print(diff)
                        print(manager_balance_after)
        else:
            super().save_model(request, obj, form, change)



@admin.register(Manager)
class ManagerAdmin(AdminViewPermissionModelAdmin):
    search_fields = ['first_name']
    filter_horizontal = ['user_permissions',]
    list_display =('pk','username','first_name','email','cellphone','actual_revenue','net_value','commission','credit_limit_to_add')
    list_editable = ('credit_limit_to_add',)
    list_display_links = ('pk','username',)


