from rest_framework.viewsets import ModelViewSet
from filters.mixins import FiltersMixin
from utils.paginations import ReleasePagination
from utils.models import Release
from utils.serializers.release import ReleaseSerializer

class ReleaseView(FiltersMixin, ModelViewSet):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    pagination_class = ReleasePagination

    filter_mappings = {
        'user':'user__pk',
        'start_creation_date': 'creation_date__gte',
        'end_creation_date': 'creation_date__lte',
    }