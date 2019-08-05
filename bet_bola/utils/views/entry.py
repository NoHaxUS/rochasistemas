from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from filters.mixins import FiltersMixin
from user.models import CustomUser
from utils.paginations import EntryPagination
from utils.models import Entry
from utils.serializers.entry import EntrySerializer
from utils.permissions import EntryPermission
import json
from core.cacheMixin import CacheKeyGetMixin

class EntryView(CacheKeyGetMixin, FiltersMixin, ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    pagination_class = EntryPagination
    permission_classes = [EntryPermission, ]
    cache_group = 'general_configurations_adm'
    caching_time = 60

    filter_mappings = {
        'user':'user__pk',
        'start_creation_date': 'creation_date__gte',
        'end_creation_date': 'creation_date__lte',
    }

    def list(self, request, pk=None):        
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)                        
                
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return Entry.objects.filter(user=user).order_by('-creation_date')
        elif user.user_type == 3:
            return Entry.objects.filter(Q(user=user.pk) | Q(user__in=user.manager.manager_assoc.all())).order_by('-creation_date')
        return Entry.objects.filter(store=user.my_store).order_by('-creation_date')
        
    def create(self, request, *args, **kwargs):        
        data = request.data.get('data')
        data = json.loads(data)
        if request.user.user_type == 2:
            data = {"user":request.user.pk, "value":data.get("value"), "description":data.get("description"), "store":request.user.my_store.pk}         
        else:    
            data = {"user":int(data.get("user")), "value":data.get("value"), "description":data.get("description"), "store":request.user.my_store.pk}         
        serializer = self.get_serializer(data=data)        
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)                        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)