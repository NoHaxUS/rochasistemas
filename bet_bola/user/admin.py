from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from user.models import CustomUser
from core.models import BetTicket
from .models import Punter, Seller, Manager
from utils.models import GeneralConfigurations
from django.contrib import messages

admin.site.register(GeneralConfigurations)


@admin.register(Punter)
class PunterAdmin(admin.ModelAdmin):
    search_fields = ['first_name']
    list_display = ('pk','first_name')
    exclude = ('user_permissions','groups',)
    list_display_links = ('pk','first_name')

@admin.register(Seller)
class SellerAdmin(GuardedModelAdmin):
    search_fields = ['first_name']
    exclude = ('user_permissions','groups',)
    list_editable = ('credit_limit',)
    list_display = ('pk','username','full_name','actual_revenue','net_value','commission','credit_limit')
    list_display_links = ('pk','username',)


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(my_manager=request.user)

    def save_model(self, request, obj, form, change):
        from pprint import pprint
        pprint(self)
      
        if request.user.has_perm('user.be_manager'):
            if form.is_valid():
                if obj.my_manager.pk == request.user.pk:
                    seller = Seller.objects.get(pk=obj.pk)
                    manager = obj.my_manager

                    print(manager.credit_limit_to_add)

                    diff = obj.credit_limit - seller.credit_limit

                    manager_balance_after = manager.credit_limit_to_add - diff

                    if manager_balance_after < 0:
                        messages.warning(request, 'Você não tem saldo suficiente.')
                        obj.status = 'NO'
                    else:
                        manager.credit_limit_to_add -= diff
                        manager.save()
                        super().save_model(request, obj, form, change)
                    print(diff)
                    print(manager_balance_after)

                
            
        #super().save_model(request, obj, form, change)

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    search_fields = ['first_name']
    filter_horizontal = ['user_permissions',]
    list_display =('pk','username','first_name','email','cellphone','actual_revenue','net_value','commission','credit_limit_to_add')
    list_editable = ('credit_limit_to_add',)
    list_display_links = ('pk','username',)
