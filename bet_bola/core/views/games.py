from django_filters import rest_framework as filters
from django.db.models import Q, F, FilteredRelation, Count, Prefetch
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters as drf_filters
from rest_framework import status
from filters.mixins import FiltersMixin
from utils.models import ExcludedLeague, ExcludedGame, MarketModified, MarketRemotion
from user.permissions import IsAdmin
from core.models import *
from core.serializers.game import TodayGamesSerializer, GameSerializer, GameListSerializer, GameTableSerializer
from core.paginations import StandardSetPagination, GameListPagination, GameTablePagination
from core.permissions import StoreIsRequired
from rest_framework.decorators import action
import utils.timezone as tzlocal
from django.conf import settings
from core.cacheMixin import CacheKeyDispatchMixin
import json


class TodayGamesView(CacheKeyDispatchMixin, ModelViewSet):
    """
    View Used for display today able games in Homepage
    """ 
    permission_classes = []
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination
    
    cache_group = 'today_games'
    caching_time = 60 * 3
    

    def get_queryset(self):
        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.game.id for excluded_games in GameModified.objects.filter(store=store, available=False)]

        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(id__in=id_list_excluded_games)\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', 
        filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)
        
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store_id)]
        id_list_excluded_locations = [excluded_locations.location.id for excluded_locations in LocationModified.objects.filter(available=False, store=store_id)]        
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)
        queryset = queryset.exclude(location__pk__in=id_list_excluded_locations)

        return queryset


class TomorrowGamesView(CacheKeyDispatchMixin, ModelViewSet):        
    """
    View Used for display tomorrow able games
    """ 
    permission_classes = []
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination

    cache_group = 'tomorrow_games'
    caching_time = 60 * 5

    def get_queryset(self):
        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_cotation_qs = Cotation.objects.filter(market__name="1X2")
    
        my_games_qs = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(id__in=id_list_excluded_games)\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', 
        queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store_id)]
        id_list_excluded_locations = [excluded_locations.location.id for excluded_locations in LocationModified.objects.filter(available=False, store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)
        queryset = queryset.exclude(location__pk__in=id_list_excluded_locations)
        return queryset


class AfterTomorrowGamesView(CacheKeyDispatchMixin, ModelViewSet):        
    """
    View Used for display after tomorrow able games
    """ 
    permission_classes = []
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination

    cache_group = 'after_tomorrow_games'
    caching_time = 60 * 5

    def get_queryset(self):
        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_cotation_qs = Cotation.objects.filter(market__name="1X2")
    
        my_games_qs = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(id__in=id_list_excluded_games)\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store_id)]
        id_list_excluded_locations = [excluded_locations.location.id for excluded_locations in LocationModified.objects.filter(available=False, store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)
        queryset = queryset.exclude(location__pk__in=id_list_excluded_locations)

        return queryset


class SearchGamesView(CacheKeyDispatchMixin, ModelViewSet):
    """
    This views is used to in search requests and filtering games from league ID
    """
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination
    permission_classes = []
    cache_group = 'search_games'
    caching_time = 60 * 3

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store_id)]
        id_list_excluded_locations = [excluded_locations.location.id for excluded_locations in LocationModified.objects.filter(available=False, store=store_id)]        

        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(), status__in=[0], available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(id__in=id_list_excluded_games)\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)
        
        if self.request.GET.get('game_name'):
            game_name = self.request.GET.get('game_name')
            my_games_qs = my_games_qs.filter(name__icontains=game_name)
            queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
            
            queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
            .filter(games_count__gt=0)
            queryset = queryset.exclude(id__in=id_list_excluded_leagues)
            queryset = queryset.exclude(location__pk__in=id_list_excluded_locations)
            return queryset

        if self.request.GET.get('league_id'):
            league_id = self.request.GET.get('league_id')
            queryset = League.objects.filter(pk=league_id).prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
            
            queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
            .filter(games_count__gt=0)
            queryset = queryset.exclude(id__in=id_list_excluded_leagues)
            queryset = queryset.exclude(location__pk__in=id_list_excluded_locations)
            return queryset      

        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
    
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)
        queryset = queryset.exclude(location__pk__in=id_list_excluded_locations)
        return queryset


class GamesTable(ModelViewSet):
    """
    View Used for display the Games Table
    """ 
    queryset = League.objects.none()
    permission_classes = []
    serializer_class = GameTableSerializer
    pagination_class = GameTablePagination
    cache_group = 'games_table'
    caching_time = 60 * 3


    def get_queryset(self):        
        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_cotation_qs = Cotation.objects.filter(Q(market__name="1X2") | Q(market__name="Dupla Chance"))

        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2') | Q(cotations__market__name="Dupla Chance") ))\
            .filter(cotations_count__gte=3)
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', 
        filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        return queryset


class TodayGamesAdmin(FiltersMixin, ModelViewSet):
    queryset = Game.objects.none()
    serializer_class = GameListSerializer
    pagination_class = GameListPagination
    

    filter_mappings = {
		'game_name':'name__icontains',
		'league_name':'league__name__icontains',
		'country_name':'league__location__name__icontains',
        'start_time': 'start_date__time__gte'
	}


    def get_queryset(self):
        store = self.request.user.my_store
    
        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store)]

        queryset = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),          
            status__in=[0])\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) | 
                Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)
        return queryset


    @action(methods=['post'], detail=False, permission_classes=[IsAdmin])
    def toggle_availability(self, request, pk=None):
        data = request.data.get('data')        
        data = json.loads(data)
        game_id = data.get('id')
        available = data.get('available')
        user = request.user
        
        invalidate_cache_group('today_games', request.user.my_store.pk)
        invalidate_cache_group('tomorrow_games', request.user.my_store.pk)
        invalidate_cache_group('after_tomorrow_games', request.user.my_store.pk)
        invalidate_cache_group('search_games', request.user.my_store.pk)    
        invalidate_cache_group('main_menu', request.user.my_store.pk) 

        if GameModified.objects.filter(game__pk=game_id, store=user.my_store).exists():
            GameModified.objects.filter(game__pk=game_id, store=user.my_store).update(available=available)
        else:
            GameModified.objects.create(game=Game.objects.get(pk=game_id), store=user.my_store, available=available)
        
        return Response({
                'success': True,
                'message': 'Alterado com Sucesso :)'
            })


class GamesTomorrowAdmin(FiltersMixin, ModelViewSet):
    """
    View Used for display tomorrow games
    """ 
    permission_classes = []
    serializer_class = GameListSerializer
    pagination_class = GameListPagination


    filter_mappings = {
		'game_name':'name__icontains',
		'league_name':'league__name__icontains',
		'country_name':'league__location__name__icontains',
        'start_time': 'start_date__time__gte'
	}

    def get_queryset(self):
        #my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store = self.request.user.my_store

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store)]

        queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
            status__in=[0])\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) | 
                Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)

        return queryset


class GamesAfterTomorrowAdmin(FiltersMixin, ModelViewSet):
    """
    View Used for display after tomorrow games
    """ 
    permission_classes = []
    serializer_class = GameListSerializer
    pagination_class = GameListPagination


    filter_mappings = {
		'game_name':'name__icontains',
		'league_name':'league__name__icontains',
		'country_name':'league__location__name__icontains',
        'start_time': 'start_date__time__gte'
	}

    def get_queryset(self):
        #my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store = self.request.user.my_store

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store)]

        queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
            status__in=[0])\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) | 
                Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)
            
        return queryset