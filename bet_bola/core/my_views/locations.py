from rest_framework.viewsets import ModelViewSet
from core.models import Location
from core.serializers.location import LocationSerializer
from core.permissions import StoreIsRequired
from core.paginations import StandardSetPagination
from filters.mixins import FiltersMixin

class LocationView(FiltersMixin, ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [StoreIsRequired,]
    pagination_class = StandardSetPagination

    filter_mappings = {
        'location_name':'name__icontains'        
    }

