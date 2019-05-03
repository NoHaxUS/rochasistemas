
class MarketReductionView(ModelViewSet):
	queryset = MarketReduction.objects.all()
	serializer_class = MarketReductionSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		markets_reduction= MarketReduction.objects.filter(store=store)
		serializer = self.get_serializer(markets_reduction, many=True)

		return Response(serializer.data)


class MarketRemotionView(ModelViewSet):
	queryset = MarketRemotion.objects.all()
	serializer_class = MarketRemotionSerializer

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		markets_remotion= MarketRemotion.objects.filter(store=store)
		serializer = self.get_serializer(markets_remotion, many=True)

		return Response(serializer.data)
