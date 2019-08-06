from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from user.permissions import IsAdmin
from utils.serializers.configuration import GeneralConfigurationsSerializer
from utils.models import GeneralConfigurations
from filters.mixins import FiltersMixin
import json
from utils.cache import invalidate_cache_group


class GeneralConfigurationsView(FiltersMixin, ModelViewSet):
	queryset = GeneralConfigurations.objects.all()
	serializer_class = GeneralConfigurationsSerializer
	permission_classes = []	

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

		invalidate_cache_group('today_games', request.user.my_store.pk)
		invalidate_cache_group('tomorrow_games', request.user.my_store.pk)
		invalidate_cache_group('after_tomorrow_games', request.user.my_store.pk)
		invalidate_cache_group('search_games', request.user.my_store.pk)
		invalidate_cache_group('market_cotation_view', request.user.my_store.pk) 

		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)