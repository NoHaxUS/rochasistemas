from django.contrib import admin
from user.models import Seller, Manager, Admin


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    pass

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    pass

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    pass