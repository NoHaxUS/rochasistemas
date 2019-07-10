from rest_framework.viewsets import ModelViewSet
from core.models import League
from core.serializers.league import LeagueSerializer
from core.permissions import StoreIsRequired
from core.paginations import StandardSetPagination
from filters.mixins import FiltersMixin


class LeagueView(FiltersMixin, ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = []
    pagination_class = StandardSetPagination

    filter_mappings = {
        'game_name':'my_games__name__icontains',        
        'league_name': 'name__icontains',
        'location_name': 'location__name__icontains'
    }
