from django.contrib import admin
from .models import Punter, Seller
# Register your models here.


@admin.register(Punter,Seller)
class PunterAdmin(admin.ModelAdmin):
	title = ('Punter','Seller')

	fieldsets = (
        (None, {
            'fields': ('first_name','last_name','username','password','email','date_joined','birthday')
        }),
      
    )