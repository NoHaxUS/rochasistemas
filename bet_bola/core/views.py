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
from .models import *
from .serializers import *


class StoreView(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class CotationHistoryView(ModelViewSet):
    queryset = CotationHistory.objects.all()
    serializer_class = CotationHistorySerializer


class SportView(ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer


class GameView(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class LeagueView(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer


class LocationView(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class CotationView(ModelViewSet):
    queryset = Cotation.objects.exclude(market__name='1X2')
    serializer_class = CotationSerializer   
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('game__id',)


class MarketView(ModelViewSet):
    queryset = Market.objects.exclude(cotations__market__name='1X2').distinct()
    serializer_class = MarketSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('cotations__game__id',)


class APIRootView(APIView):
    def get(self, request):        
        data = {                          
            'sellers': reverse('user:seller-list', request=request),           
            'managers': reverse('user:manager-list', request=request),
            'punters': reverse('user:punter-list', request=request),   
            'tickets': reverse('ticket:ticket-list', request=request),                         
            'games': reverse('core:game-list', request=request),
            'leagues': reverse('core:league-list', request=request),
            'locations': reverse('core:location-list', request=request),
            'today_games': reverse('core:today_games', request=request),
            'tomorrow_games': reverse('core:tomorrow_games', request=request),
        }
        return Response(data)


#Extras

class MainMenu(APIView):
    def get(self, request):
        games = Game.objects.filter(start_date__gt=tzlocal.now(),
        league__isnull=False,
        game_status__in=[1,8,9],
        visible=True)\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3)\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
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


class TodayGamesView(ModelViewSet):     
    my_qs = Cotation.objects.filter(market__name="1X2")
    queryset = Game.objects.filter(start_date__gt=tzlocal.now(),
        start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
        game_status__in=[1,8,9],
        visible=True)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3).order_by('-league__location__priority',
        '-league__priority', 'league__location__name', 'league__name')
    

    def list(self, request, pk=None):
        from utils.models import ExcludedGame,ExcludedLeague

        store_id = request.GET['store']
        store = Store.objects.get(pk=store_id)

        id_list_excluded_games = [excluded_games.game.id for excluded_games in ExcludedGame.objects.filter(store=store)]
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store)]
        
        
        page = self.paginate_queryset(self.queryset.exclude(id__in=id_list_excluded_games).exclude(league__id__in=id_list_excluded_leagues))
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)




    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name',)
            

# class TodayGamesView(APIView):
    
#     def get(self, request):
#         my_qs = Cotation.objects.filter(market__name="1X2")
#         queryset = Game.objects.filter(start_date__gt=tzlocal.now(),
#         start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
#         game_status__in=[1,8,9],
#         visible=True)\
#         .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
#         .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
#         .annotate(cotations_count=Count('cotations'))\
#         .filter(cotations_count__gte=3).order_by('-league__location__priority',
#         '-league__priority', 'league__location__name', 'league__name')

        
#         data = GameViewSerializer(list(queryset.values()), many=True).data
#         return Response(data)


class TomorrowGamesView(ModelViewSet):     
    my_qs = Cotation.objects.filter(market__name="1X2")
    queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),        
        game_status__in=[1,8,9],
        visible=True)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3).order_by('-league__location__priority','-league__priority')

    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name','league__name')


class AfterTomorrowGamesView(ModelViewSet):     
    my_qs = Cotation.objects.filter(market__name="1X2")
    queryset = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
        game_status__in=[1,8,9],
        visible=True)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3).order_by('-league__location__priority','-league__priority')

    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (drf_filters.SearchFilter,)
    search_fields = ('name',)


