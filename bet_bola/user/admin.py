from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Punter, Seller, GeneralConfigurations, Manager
# Register your models here.


@admin.register(Punter)
class PunterAdmin(admin.ModelAdmin):

	search_fields = ['first_name']
	search_fields_hint = 'Buscar pelo nome'

	fieldsets = (
		(None, {
			'fields': ('first_name','last_name','username','password','email','cellphone')
		}),
		)

@admin.register(Seller)
class SellerAdmin(GuardedModelAdmin):
	search_fields = ['first_name']
	search_fields_hint = 'Buscar pelo nome'

	fieldsets = (
		(None, {
			'fields': ('first_name','last_name','cpf','username','password','email','cellphone')
		}),
	)
	list_display =('pk','username','full_name','actual_revenue')


@admin.register(GeneralConfigurations)
class GeneralConfigurationsAdmin(admin.ModelAdmin):
	pass

@admin.register(Manager)
class ManagerAdmin(GuardedModelAdmin):
	search_fields = ['first_name']
	search_fields_hint = 'Buscar pelo nome'

	fieldsets = (
		(None, {
			'fields': ('first_name','last_name','username','password','email','cellphone')
		}),
		)	

