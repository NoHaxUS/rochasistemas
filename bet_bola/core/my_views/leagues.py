from rest_framework.viewsets import ModelViewSet
from core.models import League
from core.serializers.league import LeagueSerializer
from core.permissions import StoreIsRequired


class LeagueView(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [StoreIsRequired,]

