from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import filters as drf_filters
from django.db.models import Prefetch
from django.db.models import Q, FilteredRelation
from django.db.models import Count 
import utils.timezone as tzlocal
from django_filters import rest_framework as filters
from utils.models import ExcludedLeague, ExcludedGame
from .models import *


class APIRootView(APIView):
    def get(self, request):        
        data = {                          
            'stores': reverse('core:store-list', request=request),           
            'configurations': reverse('utils:generalconfigurations-list', request=request),           
            'sellers': reverse('user:seller-list', request=request),           
            'managers': reverse('user:manager-list', request=request),
            'punters': reverse('user:punter-list', request=request),   
            'tickets': reverse('ticket:ticket-list', request=request),                                     
            'leagues': reverse('core:league-list', request=request),
            'locations': reverse('core:location-list', request=request),
            'today_games': reverse('core:today_games', request=request),
            'tomorrow_games': reverse('core:tomorrow_games', request=request),
            'cotationsmodified': reverse('core:cotationmodified-list', request=request)
        }
        return Response(data)



class MainMenu(APIView):
    def get(self, request):        
        store_id = request.GET['store']        

        id_list_excluded_games = [excluded_games.game.id for excluded_games in ExcludedGame.objects.filter(store__id=store_id)]
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in ExcludedLeague.objects.filter(store=store_id)]

        games = Game.objects.filter(start_date__gt=tzlocal.now(),
        league__isnull=False,
        status__in=[0],
        available=True)\
        .annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gte=3)\
        .exclude(Q(league__available=False) | Q(league__location__available=False) | Q(league__id__in=id_list_excluded_leagues) | Q(id__in=id_list_excluded_games))\
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

