from django.db.models import Q, F, FilteredRelation, Count, Prefetch
from core.models import *
import utils.timezone as tzlocal

def games_in_zone(store):
    id_games_in_zone = [game_in_zone.game.id for game_in_zone in GameModified.objects.filter(store=store, available=True,is_in_zone=True)]

    my_cotation_qs = Cotation.objects.filter(market__name="1X2")

    my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
        id__in=id_games_in_zone,
        status__in=[0],
        available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3) 
    
    if id_games_in_zone:         
        zone_league = League(name="Jogos em Destaques")
        zone_league.games = my_games_qs            
        return zone_league

    return None