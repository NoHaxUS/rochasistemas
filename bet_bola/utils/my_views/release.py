from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from filters.mixins import FiltersMixin
from user.models import CustomUser
from utils.paginations import ReleasePagination
from utils.models import Release
from utils.serializers.release import ReleaseSerializer
from utils.permissions import ReleasePermission
import json

class ReleaseView(FiltersMixin, ModelViewSet):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
    pagination_class = ReleasePagination
    permission_classes = [ReleasePermission, ]

    filter_mappings = {
        'user':'user__pk',
        'start_creation_date': 'creation_date__gte',
        'end_creation_date': 'creation_date__lte',
    }

    def create(self, request, *args, **kwargs):        
        data = request.data.get('data')
        data = json.loads(data)
        data = {"user":int(data.get("user")), "value":data.get("value")}         
        serializer = self.get_serializer(data=data)        
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)                        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)