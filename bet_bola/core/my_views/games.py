from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters as drf_filters
from filters.mixins import FiltersMixin
from django.db.models import Q, F, FilteredRelation, Count, Prefetch
import utils.timezone as tzlocal
from django_filters import rest_framework as filters
from utils.models import ExcludedLeague, ExcludedGame
from core.models import *
from core.serializers.game import TodayGamesSerializer, GameSerializer, GameListSerializer, GameTableSerializer
from core.paginations import StandardSetPagination, GameListPagination
from core.permissions import StoreIsRequired
from rest_framework.decorators import action


class TodayGamesView(ModelViewSet):
    """
    View Used for display today able games in Homepage
    """ 
    permission_classes = []
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination

    def list(self, request, pk=None):
        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', 
        filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


class TomorrowGamesView(ModelViewSet):        
    """
    View Used for display tomorrow able games
    """ 
    permission_classes = []
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination

    def list(self, request, pk=None):
        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_cotation_qs = Cotation.objects.filter(market__name="1X2")
    
        my_games_qs = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', 
        queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


class AfterTomorrowGamesView(ModelViewSet):        
    """
    View Used for display after tomorrow able games
    """ 
    permission_classes = []
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination

    def list(self, request, pk=None):
        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_cotation_qs = Cotation.objects.filter(market__name="1X2")
    
        my_games_qs = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


class SearchGamesView(ModelViewSet):
    """
    This views is used to in search requests from HomePage
    """
    serializer_class = TodayGamesSerializer
    pagination_class = GameListPagination
    permission_classes = []

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__available=False) | Q(league__location__available=False) | Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        if self.request.GET.get('game'):
            game_name = self.request.GET.get('game')
            my_games_qs = my_games_qs.filter(name__icontains=game_name)
            queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
            
            queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
            .filter(games_count__gt=0)
            queryset = queryset.exclude(id__in=id_list_excluded_leagues)
            return queryset        

        queryset = League.objects.prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
    
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)
        return queryset




class TodayGames(FiltersMixin, ModelViewSet):
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
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),          
            status__in=[0])\
            .exclude(Q(league__available=False) | 
                Q(league__location__available=False) | 
                Q(id__in=id_list_excluded_games) | 
                Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset


    @action(methods=['post'], detail=False, permission_classes=[])
    def toggle_availability(self, request, pk=None):
        response = []
        for game in Game.objects.filter(pk__in=dict(request.data)['data']):
            response.append(game.toggle_availability())
        return Response(response)


class GamesTable(ModelViewSet):
    serializer_class = GameTableSerializer
    pagination_class = StandardSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(Q(market__name="1X2") | Q(market__name="Dupla Chance"))

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),          
            status__in=[0],
            available=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__available=False) | Q(league__location__available=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=(Q(cotations__market__name='1X2') | Q(cotations__market__name="Dupla Chance"))))\
            .filter(cotations_count__gte=6).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset


class GamesTomorrow(ModelViewSet):
    serializer_class = GameListSerializer
    pagination_class = GameListPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),          
            status__in=[0])\
            .exclude(Q(league__available=False) | Q(league__location__available=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset


class GamesAfterTomorrow(ModelViewSet):
    serializer_class = GameListSerializer
    pagination_class = GameListPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),                      
            status__in=[0])\
            .exclude(Q(league__available=False) | Q(league__location__available=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset

