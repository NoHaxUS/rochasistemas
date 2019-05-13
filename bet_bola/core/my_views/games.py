from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters as drf_filters
from django.db.models import Q, F, FilteredRelation, Count, Prefetch
import utils.timezone as tzlocal
from django_filters import rest_framework as filters
from utils.models import ExcludedLeague, ExcludedGame
from core.models import *
from core.serializers.game import LeagueGameSerializer, GameSerializer, GameTableSerializer
from core.paginations import StandardResultsSetPagination
from core.permissions import StoreIsRequired


class GamesToday(ModelViewSet):
    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),          
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset

class GamesTable(ModelViewSet):
    serializer_class = GameTableSerializer
    pagination_class = StandardResultsSetPagination
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
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=(Q(cotations__market__name='1X2') | Q(cotations__market__name="Dupla Chance"))))\
            .filter(cotations_count__gte=6).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset


class GamesTomorrow(ModelViewSet):
    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),          
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset


class GamesAfterTomorrow(ModelViewSet):
    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')

    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),                      
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_leagues) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        return queryset


class GameAbleView(ModelViewSet):

    serializer_class = LeagueGameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')
    
    permission_classes = [StoreIsRequired,]
        
    def list(self, request, pk=None):            
        
        queryset = self.get_queryset()        
        page = self.paginate_queryset(queryset)                
            
        if page is not None:            
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = self.request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        if self.request.GET.get('game'):
            game_name = self.request.GET.get('game')
            my_games_qs = my_games_qs.filter(name__icontains=game_name)
            queryset = League.objects.all().prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
            queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__start_date__gt=tzlocal.now(),my_games__start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),my_games__game_status=0, my_games__name__icontains=game_name)))\
            .filter(games_count__gt=0)            

            queryset = queryset.exclude(id__in=id_list_excluded_leagues)
            return queryset        

        queryset = League.objects.all().prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
    
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__start_date__gt=tzlocal.now(),my_games__start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),my_games__game_status=0)))\
        .filter(games_count__gt=0)

        return queryset

class TodayGamesView(ModelViewSet):         
    queryset = League.objects.all()
    permission_classes = [StoreIsRequired,]
        
    def list(self, request, pk=None):        
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             


        my_games_qs = Game.objects.filter(start_date__gt=tzlocal.now(),
            start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        queryset = League.objects.all().prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
                        
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)
        
        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                
        
        if request.GET.get('game'):            
            page = self.paginate_queryset(queryset.filter(my_games__name__icontains=request.GET.get('game')))            

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)



    serializer_class = LeagueGameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')
            

class TomorrowGamesView(ModelViewSet):             
    queryset = League.objects.all()
    permission_classes = [StoreIsRequired,]
               
    def list(self, request, pk=None):        
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             

        my_games_qs = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        queryset = League.objects.all().prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)

        for game in queryset.all():
            print(str(game.games_count))

        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                

        if request.GET.get('game_id'):
            page = self.paginate_queryset(queryset.filter(Q(name__icontains=request.GET.get('game_id'))))                    

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)



    serializer_class = LeagueGameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')


class AfterTomorrowGamesView(ModelViewSet):         
    queryset = League.objects.all()
    permission_classes = [StoreIsRequired,]

    def list(self, request, pk=None):        
        my_cotation_qs = Cotation.objects.filter(market__name="1X2")

        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.id for excluded_games in ExcludedGame.objects.filter(store=store)]             


        my_games_qs = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
            game_status__in=[0],
            visible=True)\
            .prefetch_related(Prefetch('cotations', queryset=my_cotation_qs, to_attr='my_cotations'))\
            .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) )\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3).order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')
        
        queryset = League.objects.all().prefetch_related(Prefetch('my_games', queryset=my_games_qs, to_attr='games'))
        
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__pk__in=[game.pk for game in my_games_qs])))\
        .filter(games_count__gt=0)
        
        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                

        if request.GET.get('game_id'):
            page = self.paginate_queryset(queryset.filter(Q(name__icontains=request.GET.get('game_id'))))            

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


    serializer_class = LeagueGameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')
