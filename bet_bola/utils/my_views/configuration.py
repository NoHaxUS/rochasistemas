from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from user.permissions import IsAdmin
from utils.serializers.configuration import GeneralConfigurationsSerializer
from utils.models import GeneralConfigurations
from filters.mixins import FiltersMixin
import json

class GeneralConfigurationsView(FiltersMixin, ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer
    permission_classes = [IsAdmin,]

    filter_mappings = {
		'store':'store__pk',		
  	}

    def list(self, request, pk=None):		
      if request.user.is_authenticated:
        store_id = request.user.my_store.pk			
        general_configuration= GeneralConfigurations.objects.filter(store__pk=store_id)
        serializer = self.get_serializer(general_configuration, many=True)
        return Response(serializer.data)
      return Response({})    

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