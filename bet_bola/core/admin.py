from django.contrib import admin
from core.models import Store, Game


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['pk','name']