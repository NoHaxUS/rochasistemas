from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from user.models import CustomUser
from core.models import BetTicket
from .models import Punter, Seller, Manager
from utils.models import GeneralConfigurations
from guardian.shortcuts import get_objects_for_user

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

        manager = CustomUser.objects.get(pk=request.user.pk)
        print(manager)
        qs = get_objects_for_user(manager, 'user.set_credit_limit')
        print(qs)
        return qs

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    search_fields = ['first_name']
    filter_horizontal = ['user_permissions',]
    list_display =('pk','username','first_name','email','cellphone','actual_revenue','net_value','commission','credit_limit_to_add')
    list_editable = ('credit_limit_to_add',)
    list_display_links = ('pk','username',)