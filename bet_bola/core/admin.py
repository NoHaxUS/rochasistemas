from django.contrib import admin
from core.models import Store, Game, Cotation

class NeededGames(admin.SimpleListFilter):
    title = 'Jogos Importantes'
    parameter_name = 'needed'

    def lookups(self, request, model_admin):
        return (
            ('Sim', 'Sim'),
            ('Não', 'Não')
        )

    def queryset(self, request, queryset):
        if self.value() == 'Sim':
            return queryset.filter(pk=81573711)
        return queryset


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass

@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
    search_fields = ['pk','name']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['pk','name']
    list_filter = (NeededGames,)