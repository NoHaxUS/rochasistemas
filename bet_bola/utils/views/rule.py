
class RulesMessageView(ModelViewSet):
	queryset = RulesMessage.objects.all()
	serializer_class = RulesMessageSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rules= RulesMessage.objects.filter(store=store)
		serializer = self.get_serializer(rules, many=True)

		return Response(serializer.data)
        