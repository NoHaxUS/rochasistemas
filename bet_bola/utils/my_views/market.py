from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from user.permissions import IsAdmin
from utils.serializers.market import MarketReductionSerializer, MarketRemotionSerializer, GetMarketRemotionSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import MarketReduction, MarketRemotion
import json

class MarketReductionView(ModelViewSet):
	queryset = MarketReduction.objects.all()
	serializer_class = MarketReductionSerializer
	permission_classes = [IsAdmin,]

	def list(self, request, pk=None):
		if request.user.is_authenticated:
			store_id = request.user.my_store.pk			
			markets_reduction= MarketReduction.objects.filter(store__pk=store_id)
			serializer = self.get_serializer(markets_remotion, many=True)
			return Response(serializer.data)
		return Response({})	
	
	def perform_create(self, serializer):		
		store = self.request.user.my_store
		market = serializer.validated_data['market']
		reduction_percentual = serializer.validated_data['reduction_percentual']
		active = serializer.validated_data['active']
		if MarketReduction.objects.filter(store=store, market=market).exists():
			markets_reduction = MarketReduction.objects.get(store=store, market=market)
			markets_reduction.reduction_percentual = reduction_percentual
			markets_reduction.active = active
			markets_reduction.save()
			return markets_reduction		
		return MarketReduction.objects.create(store=store, market=market, reduction_percentual=reduction_percentual, active=active)


class MarketRemotionView(ModelViewSet):
	queryset = MarketRemotion.objects.all()	
	permission_classes = [IsAdmin,]

	def create(self, request, *args, **kwargs):
		data = request.data.get('data')    		
		if not data:
			data = "{}"
		data = json.loads(data)        
		data['store'] = self.request.user.my_store.pk
		serializer = self.get_serializer(data=data)               
		serializer.is_valid(raise_exception=True)        
		self.perform_create(serializer)                
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
	
	def list(self, request, pk=None):
		if request.user.is_authenticated:
			store_id = request.user.my_store.pk			
			markets_remotion= MarketRemotion.objects.filter(store__pk=store_id)			
			serializer = self.get_serializer(markets_remotion, many=True)
			return Response(serializer.data)
		return Response({})					

	def get_serializer_class(self):
		if self.request.method in SAFE_METHODS:
			return GetMarketRemotionSerializer
		return MarketRemotionSerializer