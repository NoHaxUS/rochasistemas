

class RewardRelatedView(ModelViewSet):
	queryset = RewardRelated.objects.all().order_by('value_max','pk')
	serializer_class = RewardRelatedSerializer
	permission_classes = [General,]


	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rewards_related= RewardRelated.objects.filter(store=store)
		serializer = self.get_serializer(rewards_related, many=True)

		return Response(serializer.data)


