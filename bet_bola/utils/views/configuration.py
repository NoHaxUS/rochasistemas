from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from user.permissions import IsAdmin
from utils.serializers.configuration import GeneralConfigurationsSerializer
from utils.models import GeneralConfigurations
from filters.mixins import FiltersMixin
import json
from core.cacheMixin import CacheKeyGetMixin

class GeneralConfigurationsView(CacheKeyGetMixin, FiltersMixin, ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer
    permission_classes = []
    cache_group = 'general_configurations_adm'
    caching_time = 60

    filter_mappings = {
      'store':'store__pk',		
    }
    
    def get_queryset(self):
        store = self.request.user.my_store
        return self.queryset.filter(store=store)

    def create(self, request, *args, **kwargs):
      data = request.data.get('data')       
      if not data:
          data = "{}"       
      data = json.loads(data)             
      serializer = self.get_serializer(data=data)               
      serializer.is_valid(raise_exception=True)        
      self.perform_create(serializer)                
      headers = self.get_success_headers(serializer.data)
      return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)