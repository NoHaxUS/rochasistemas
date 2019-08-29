from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Count 
from django_filters import rest_framework as filters
from core.models import League, Game, Location, LeagueModified, LocationModified, GameModified
from core.serializers.location import MenuViewSerializer
from core.cacheMixin import  CacheKeyDispatchMixin
from core.models import Cotation
import utils.timezone as tzlocal
from django.conf import settings
from utils.utils import sort_by_priority_menu
import json

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


class MainMenu(CacheKeyDispatchMixin, ModelViewSet):
    serializer_class = MenuViewSerializer
    caching_time = 60
    cache_group = 'main_menu'        

    def get_queryset(self):        
        store_id = self.request.GET['store']

        id_list_excluded_games = [excluded_games.game.id for excluded_games in GameModified.objects.filter(store__id=store_id)]
        id_list_excluded_leagues = [excluded_leagues.league.id for excluded_leagues in LeagueModified.objects.filter(available=False, store=store_id)]
        id_list_excluded_locations = [excluded_locations.location.id for excluded_locations in LocationModified.objects.filter(available=False, store=store_id)]

        games = Game.objects.filter(start_date__gt=tzlocal.now(),
            status__in=[0],
            available=True).exclude(id__in=id_list_excluded_games)\
            .annotate(cotations_count=Count('cotations', filter=Q(cotations__market__name='1X2')))\
            .filter(cotations_count__gte=3)\
            .exclude(Q(league__location__pk__in=id_list_excluded_locations) | Q(league__id__in=id_list_excluded_leagues) | Q(id__in=id_list_excluded_games))                

        leagues = League.objects.filter(my_games__in=games).distinct()
        my_location_mods = LocationModified.objects.filter(store__id=store_id)

        location = Location.objects.filter(my_leagues__in=leagues)\
        .prefetch_related(Prefetch('my_leagues', queryset=leagues, to_attr='leagues'),
            Prefetch('my_modifications', queryset=my_location_mods, to_attr='modifications')
        )

        return sorted(location.distinct(), key=sort_by_priority_menu, reverse=True)


class ChangePassword(APIView):

    def post(self, request):
        data = json.loads(request.POST.get("data"))
        if request.user.check_password(data.get("old_password")):
            if data.get("new_password") == data.get("password_confirmation"):
                request.user.set_password(data.get("new_password"))
                request.user.save()
                return Response({"success":True})
            else:                
                return Response({
                    "success":False,
                    "message":"Confirmação de senha não é compatível com a nova senha."
                    })
        
        return Response({
                    "success":False,
                    "message":"Senha atual incorreta."
                    })