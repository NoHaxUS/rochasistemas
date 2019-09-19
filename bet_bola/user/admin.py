from django.contrib import admin
from user.models import Seller, Manager, Admin, TicketOwner, CustomUser


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    fields = ('username','first_name','password','user_type','my_store','cellphone', 'email','cpf','address','can_sell_unlimited','credit_limit','can_cancel_ticket','limit_time_to_cancel','comission_based_on_profit','can_change_limit_time','is_active')

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    fields = ('username','first_name','password','user_type','my_store','cellphone', 'email','is_active')

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    fields = ('username','first_name','password','user_type','my_store','cellphone', 'email','cpf','address','can_sell_unlimited','credit_limit','my_manager','can_cancel_ticket','limit_time_to_cancel','is_active')
    autocomplete_fields = ('my_manager',)

@admin.register(TicketOwner)
class TicketOwnerAdmin(admin.ModelAdmin):
    search_fields = ('first_name',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username',)

