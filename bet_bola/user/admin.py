from django.contrib import admin
from .models import Punter, Seller, GeneralConfigurations
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
class SellerAdmin(admin.ModelAdmin):
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


