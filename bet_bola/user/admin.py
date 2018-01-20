from django.contrib import admin
from .models import Punter, Seller
# Register your models here.


@admin.register(Punter)
class PunterAdmin(admin.ModelAdmin):
	title = ('Punter')

	fieldsets = (
		(None, {
			'fields': ('first_name','last_name','username','password','email','date_joined')
		}),
		)

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
	title = ('Seller')

	fieldsets = (
		(None, {
			'fields': ('first_name','last_name','cpf','username','password','email','cellphone')
		}),
	)
	list_display =('pk','username','full_name','cellphone')


