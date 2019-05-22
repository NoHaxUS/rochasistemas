from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet
from utils.serializers.market import MarketReductionSerializer, MarketRemotionSerializer, GetMarketRemotionSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import MarketReduction, MarketRemotion

class MarketReductionView(ModelViewSet):
	queryset = MarketReduction.objects.all()
	serializer_class = MarketReductionSerializer
	permission_classes = [StoreIsRequired, UserIsFromThisStore,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		markets_reduction= MarketReduction.objects.filter(store=store)
		serializer = self.get_serializer(markets_reduction, many=True)

		return Response(serializer.data)
	
	def perform_create(self, serializer):
		store = serializer.validated_data['store']
		market = serializer.validated_data['market']
		reduction_percentual = serializer.validated_data['reduction_percentual']
		if MarketReduction.objects.filter(store=store, market=market).exists():
			markets_reduction = MarketReduction.objects.get(store=store, market=market)
			markets_reduction.reduction_percentual = reduction_percentual
			markets_reduction.save()
			return markets_reduction
		super(MarketReductionView,).perform_create(serializer)


class MarketRemotionView(ModelViewSet):
	queryset = MarketRemotion.objects.all()
	permission_classes = [StoreIsRequired]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		markets_remotion= MarketRemotion.objects.filter(store=store)
		serializer = self.get_serializer(markets_remotion, many=True)

		return Response(serializer.data)

	def get_serializer_class(self):
		if self.request.method in SAFE_METHODS:
			return GetMarketRemotionSerializer
		return MarketRemotionSerializer