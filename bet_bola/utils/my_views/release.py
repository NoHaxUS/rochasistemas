from django.db.models import Q
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

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return Release.objects.filter(user=user)            
        elif user.user_type == 3:
            return Release.objects.filter(Q(user=user.pk) | Q(user__in=user.manager.manager_assoc.all()))            
        return Release.objects.filter(store=user.my_store)
        
    def create(self, request, *args, **kwargs):        
        data = request.data.get('data')
        data = json.loads(data)
        if request.user.user_type == 2:
            data = {"user":request.user.pk, "value":data.get("value"), "store":request.user.my_store.pk}         
        else:    
            data = {"user":int(data.get("user")), "value":data.get("value"), "store":request.user.my_store.pk}         
        serializer = self.get_serializer(data=data)        
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)                        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)