from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters as drf_filters
from django.db.models import Prefetch
from django.db.models import Q, FilteredRelation
from django.db.models import Count 
import utils.timezone as tzlocal
from django_filters import rest_framework as filters
from utils.models import ExcludedLeague, ExcludedGame
from .models import *
from .serializers import *
from .permissions import General, StorePermission, CotationModifyPermission


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 80
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'results': data
        })


class StoreView(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [StorePermission,]


class CotationHistoryView(ModelViewSet):
    queryset = CotationHistory.objects.all()
    serializer_class = CotationHistorySerializer
    permission_classes = [General,]


class CotationModifiedView(ModelViewSet):
    queryset = CotationModified.objects.all()
    serializer_class = CotationModifiedSerializer
    permission_classes = [CotationModifyPermission,]


class SportView(ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [General,]


class GameView(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [General,]

    def list(self, request, pk=None):        
        store_id = request.GET['store']        

        id_list_excluded_games = [excluded_games.game.id for excluded_games in ExcludedGame.objects.filter(store__id=store_id)]
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        
        games = Game.objects.all().exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(id__in=id_list_excluded_games) | Q(league__id__in=id_list_excluded_games))\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .order_by('-league__location__priority',
            '-league__priority', 'league__location__name', 'league__name')

        page = self.paginate_queryset(games)                

        if request.GET.get('game'):
            page = self.paginate_queryset(games.filter(Q(name__icontains=request.GET.get('game'))))
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


class GameAbleView(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [General,]

    def list(self, request, pk=None):        
        store_id = request.GET['store']        

        id_list_excluded_games = [excluded_games.game.id for excluded_games in ExcludedGame.objects.filter(store__id=store_id)]
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        games = Game.objects.filter(start_date__gt=tzlocal.now(),
        league__isnull=False,
        game_status__in=[0],
        visible=True)\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3)\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(league__id__in=id_list_excluded_leagues) | Q(id__in=id_list_excluded_games))\
        .order_by('-league__location__priority', '-league__priority')\
        .values('league__location','league__location__name', 'league')\
        .distinct()
        print(games)

        page = self.paginate_queryset(games)                

        if request.GET.get('game'):
            page = self.paginate_queryset(games.filter(Q(name__icontains=request.GET.get('game'))))
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


class LeagueView(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [General,]


class LocationView(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [General,]


class CotationView(ModelViewSet):
    queryset = Cotation.objects.exclude(market__name='1X2')
    serializer_class = MinimumCotationSerializer   
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('game__id',)
    permission_classes = [General,]


class MarketView(ModelViewSet):
    queryset = Market.objects.exclude(cotations__market__name='1X2').distinct()
    serializer_class = MarketSerializer    
    permission_classes = [General,]


class APIRootView(APIView):
    def get(self, request):        
        data = {                          
            'stores': reverse('core:store-list', request=request),           
            'configurations': reverse('utils:generalconfigurations-list', request=request),           
            'sellers': reverse('user:seller-list', request=request),           
            'managers': reverse('user:manager-list', request=request),
            'punters': reverse('user:punter-list', request=request),   
            'tickets': reverse('ticket:ticket-list', request=request),                         
            'games': reverse('core:game-list', request=request),
            'leagues': reverse('core:league-list', request=request),
            'locations': reverse('core:location-list', request=request),
            'today_games': reverse('core:today_games', request=request),
            'tomorrow_games': reverse('core:tomorrow_games', request=request),
            'cotationsmodified': reverse('core:cotationmodified-list', request=request)
        }
        return Response(data)

#Extras
class MainMenu(APIView):
    def get(self, request):        
        store_id = request.GET['store']        

        id_list_excluded_games = [excluded_games.game.id for excluded_games in ExcludedGame.objects.filter(store__id=store_id)]
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        games = Game.objects.filter(start_date__gt=tzlocal.now(),
        league__isnull=False,
        game_status__in=[0],
        visible=True)\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3)\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) | Q(league__id__in=id_list_excluded_leagues) | Q(id__in=id_list_excluded_games))\
        .order_by('-league__location__priority', '-league__priority')\
        .values('league__location','league__location__name', 'league')\
        .distinct()


        itens = {}
        for value in games:
            value["league__name"] = League.objects.filter(id=value['league']).values('name').first()['name']
            if not value['league__location__name'] in itens.keys():
                itens[value['league__location__name']] = []
                itens[value['league__location__name']].append( ( value['league'], value["league__name"]) )
            else:
                itens[value['league__location__name']].append( ( value['league'], value["league__name"]) )

        return Response(itens)


class TodayGamesView(ModelViewSet):         
    queryset = League.objects.all()
    permission_classes = [General,]
        
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
        
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__start_date__gt=tzlocal.now(),my_games__start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),my_games__game_status=0)))\
        .filter(games_count__gt=0)

        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                

        if request.GET.get('game'):            
            page = self.paginate_queryset(queryset.filter(my_games__name__icontains=request.GET.get('game')))
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

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
    permission_classes = [General,]
               
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
        
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),my_games__game_status=0)))\
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
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

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
    permission_classes = [General,]

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
        
        queryset = queryset.annotate(games_count=Count('my_games', filter=Q(my_games__start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),my_games__game_status=0)))\
        .filter(games_count__gt=0)
        
        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]
        queryset = queryset.exclude(id__in=id_list_excluded_leagues)

        page = self.paginate_queryset(queryset)                

        if request.GET.get('game_id'):
            page = self.paginate_queryset(queryset.filter(Q(name__icontains=request.GET.get('game_id'))))
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


    serializer_class = LeagueGameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')


