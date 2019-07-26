from rest_framework.viewsets import ModelViewSet
from core.models import Sport
from core.permissions import StoreIsRequired
from core.serializers.sport import SportSerializer

class SportView(ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [StoreIsRequired,]

