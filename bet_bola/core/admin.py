from django.contrib import admin
from core.models import Store, Game, Cotation
from ticket.models  import Ticket
from updater.process_tickets import process_tickets
from updater.process_results_betsapi import process_games
import utils.timezone as tzlocal
from django.db.models import F
import datetime
from django.utils import timezone
from django.db.models import DateTimeField, ExpressionWrapper


class NeededGames(admin.SimpleListFilter):
    title = 'Jogos Sem Resultados*'
    parameter_name = 'needed'

    def lookups(self, request, model_admin):
        return (
            ('Sim', 'Sim'),
            ('Não', 'Não')
        )

    def queryset(self, request, queryset):
        if self.value() == 'Sim':
            return queryset.annotate(actual_start_date=ExpressionWrapper(F('start_date') + timezone.timedelta(hours=2, minutes=30 ), output_field=DateTimeField()) )\
            .filter(actual_start_date__lt=tzlocal.now(), score_half='', score_full='', results_calculated=False)
        return queryset

class FinishedGames(admin.SimpleListFilter):
    title = 'Jogos Status Terminado'
    parameter_name = 'finished'

    def lookups(self, request, model_admin):
        return (
            ('Sim', 'Sim'),
            ('Não', 'Não')
        )

    def queryset(self, request, queryset):
        if self.value() == 'Sim':
            return queryset.filter(status=3)
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
    list_filter = (NeededGames, FinishedGames)

    def save_model(self, request, obj, form, change):
        if change and obj.score_half and obj.score_full:
            game = Game.objects.get(pk=obj.pk)
            if game.score_half != obj.score_half or game.score_full != obj.score_full or game.status != obj.status:
                super().save_model(request, obj, form, change)
                games = []
                games.append(obj)
                process_games(games)
                tickets = Ticket.objects.filter(cotations__game__pk=obj.pk).distinct()
                process_tickets(tickets)
                for ticket in tickets:
                    ticket.update_ticket_reward()
                return

        super().save_model(request, obj, form, change)
      