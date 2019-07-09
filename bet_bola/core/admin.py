from django.contrib import admin
from core.models import Store, Game, Cotation
from ticket.models  import Ticket
from updater.process_tickets import process_tickets

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


def reprocess_tickets(modeladmin, request, queryset):
    for game in queryset:
        tickets = Ticket.objects.filter(cotations__game__pk=game.pk).distinct()
        process_tickets(tickets)

reprocess_tickets.short_description = 'Reprocessar Ticket(s)'


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
    actions = [reprocess_tickets,]