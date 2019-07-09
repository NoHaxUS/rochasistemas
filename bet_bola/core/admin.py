from django.contrib import admin
from core.models import Store, Game, Cotation
from ticket.models  import Ticket
from updater.process_tickets import process_tickets
from updater.process_results_betsapi import process_games

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

    def save_model(self, request, obj, form, change):
        if change:
            game = Game.objects.get(pk=obj.pk)
            if game.score_half != obj.score_half or game.score_full != obj.score_full:
                super().save_model(request, obj, form, change)
                games = []
                games.append(obj)
                process_games(games)
                tickets = Ticket.objects.filter(cotations__game__pk=obj.pk).distinct()
                process_tickets(tickets)
            else:
                super().save_model(request, obj, form, change)
        else:
            super().save_model(request, obj, form, change)