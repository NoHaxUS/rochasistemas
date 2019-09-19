from django.contrib import admin
from core.models import Store, Game, Cotation, LeagueModified
from ticket.models  import Ticket
from updater.process_tickets import process_tickets
from updater.process_results_betsapi import process_games
import utils.timezone as tzlocal
from django.db.models import F, Func, Q
import datetime
from datetime import timedelta
from django.utils import timezone
from django.db.models import DateTimeField, ExpressionWrapper

@admin.register(LeagueModified)
class LeagueModifiedAdmin(admin.ModelAdmin):
    search_fields = ['name',]

class NeededGames(admin.SimpleListFilter):
    title = 'Ticket(s) em Aberto'
    parameter_name = 'has_ticket_open'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Sim'),
            ('no', 'Não')
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            games_ids = []
            tickets = Ticket.objects.filter(status=0)
            for ticket in tickets:
                valid_cotations = ticket.cotations.filter(game__status__in = (0,1,2,3))
                has_lost_cotation = valid_cotations.filter(settlement=1)
                if not has_lost_cotation:
                    open_cotations = valid_cotations.filter(settlement=0)
                    for open_cotation in open_cotations:
                        games_ids.append(open_cotation.game.pk)
            games = Game.objects.filter(pk__in=games_ids)\
                .annotate( end_date = ExpressionWrapper(F('start_date') + timedelta(minutes=460), output_field=DateTimeField()) )\
                .filter(end_date__lte=tzlocal.now())
            return games

        return queryset

class GamesPerDay(admin.SimpleListFilter):
    title = 'Dia do Jogo'
    parameter_name = 'game_day'

    def lookups(self, request, model_admin):
        return (
            ('yesterday', 'Ontem'),
            ('today', 'Hoje'),
            ('tomorrow', 'Amanhã'),
            ('after_tomorrow', 'Depois de Amanhã')
        )

    def queryset(self, request, queryset):
        if self.value() == 'yesterday':
            return queryset.filter(
                start_date__date=tzlocal.now().date() + timezone.timedelta(days=-1)
            )
        if self.value() == 'today':
            return queryset.filter(
                start_date__date=tzlocal.now().date()
            )
        if self.value() == 'tomorrow':
            return queryset.filter(
                start_date__date=tzlocal.now().date() + timezone.timedelta(days=1)
            )
        if self.value() == 'after_tomorrow':
            return queryset.filter(
                start_date__date=tzlocal.now().date() + timezone.timedelta(days=2)
            )

        return queryset


class GamesCompletedWithNoCalulatedFlag(admin.SimpleListFilter):
    title = 'Não Calculados'
    parameter_name = 'not_calc_games'

    def lookups(self, request, model_admin):
        return (
            ('not_calc', 'Não Calculados'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'not_calc':
            return queryset.filter(
                ~Q(
                    score_half__isnull=False,
                    score_full__isnull=False
                ) |
                ~Q (
                    score_half='',
                    score_full=''
                )
            ).filter(results_calculated=False)
        return queryset


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    search_fields = ('fantasy',)

@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
    search_fields = ['pk','name']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    search_fields = ['pk','name']
    list_filter = (NeededGames, GamesPerDay, GamesCompletedWithNoCalulatedFlag)

    def save_model(self, request, obj, form, change):
        if change and obj.score_half and obj.score_full:
            game = Game.objects.get(pk=obj.pk)
            if game.score_half != obj.score_half \
            or game.score_full != obj.score_full \
            or game.status != obj.status \
            or not obj.results_calculated:
                super().save_model(request, obj, form, change)
                games = []
                games.append(obj)
                process_games(games)
                tickets = Ticket.objects.filter(cotations__game__pk=obj.pk).distinct()
                process_tickets(tickets)
                for ticket in tickets:
                    #print("Updating reward for: " + str(ticket.ticket_id))
                    ticket.update_ticket_reward()
                return

        super().save_model(request, obj, form, change)
      