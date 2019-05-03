from rest_framework.viewsets import ModelViewSet
from core.models import Location
from core.serializers.location import LocationSerializer
from core.permissions import StoreIsRequired

class LocationView(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [StoreIsRequired,]

