from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from user.permissions import IsAdmin
from core.models import League, LeagueModified
from core.serializers.league import LeagueSerializer, LeagueModifiedSerializer
from core.permissions import StoreIsRequired
from core.paginations import StandardSetPagination
from filters.mixins import FiltersMixin
from utils.cache import invalidate_cache_group
import json


class LeagueAdminView(FiltersMixin, ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = []
    pagination_class = StandardSetPagination

    filter_mappings = {
        'game_name':'my_games__name__icontains',        
        'league_name': 'name__icontains',
        'location_name': 'location__name__icontains'
    }

    def get_queryset(self):
        priority = self.request.GET.get('my_priority')
        available = self.request.GET.get('available')
        
        store = self.request.user.my_store
        qs = self.queryset.all()
        
        
        ordered_leagues = League.objects.filter(my_modifications__store=store).order_by('my_modifications__priority')        
        filtered_ids = [league.pk for league in ordered_leagues]
        qs = League.objects.exclude(pk__in=filtered_ids)
        qs = ordered_leagues | qs

        if priority:
            qs = qs.filter(my_modifications__store=store, my_modifications__priority__gt=priority) | qs.filter(priority__gt=priority).exclude(my_modifications__store=store)
        if available:
            qs = qs.filter(my_modifications__store=store, my_modifications__available=available) | qs.filter(available=available).exclude(my_modifications__store=store)
        
        return qs.distinct()



class LeagueModifiedView(FiltersMixin, ModelViewSet):
    queryset = LeagueModified.objects.all()
    serializer_class = LeagueModifiedSerializer
    permission_classes = []
    pagination_class = StandardSetPagination
    

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')        
        data = json.loads(data)        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        invalidate_cache_group(
            [
                '/today_games/',
                '/tomorrow_games/',
                '/after_tomorrow_games/',
                '/search_games/',
                '/main_menu/'
            ], 
            request.user.my_store.pk
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(methods=['post'], detail=False, permission_classes=[IsAdmin])
    def toggle_priority(self, request, pk=None):        
        data = request.data.get('data')        
        data = json.loads(data)
        ids = data.get('ids')
        value = data.get('value')
        store = request.user.my_store
        
        invalidate_cache_group(
            [
                '/today_games/',
                '/tomorrow_games/',
                '/after_tomorrow_games/',
                '/search_games/',
                '/main_menu/'
            ], 
            request.user.my_store.pk
        )

        if value:
            for id in ids:
                if LeagueModified.objects.filter(league__pk=id, store=store).exists():
                    LeagueModified.objects.filter(league__pk=id, store=store).update(priority=value)
                else:
                    LeagueModified.objects.create(priority=value, league=League.objects.get(pk=id), store=store)

            return Response({
                'success': True,
                'message': 'Alterado com Sucesso :)'
            })        

        return Response({
            'success': False,
            'message': 'Erro: Não foi possível inserir o valor'
        })