from django.contrib import admin
from core.models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass