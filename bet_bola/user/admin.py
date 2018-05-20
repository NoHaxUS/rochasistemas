from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from user.models import CustomUser
from core.models import BetTicket
from .models import Punter, Seller, GeneralConfigurations, Manager
from django.contrib.admin.models import CHANGE, ADDITION, LogEntry
# Register your models here.

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


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
	search_fields = ['first_name']
	fields = ('first_name','last_name','cpf','address','username','password','email','cellphone','credit_limit_to_add',)
	list_display =('pk','username','first_name','email','cellphone','actual_revenue','net_value','commission','credit_limit_to_add')
