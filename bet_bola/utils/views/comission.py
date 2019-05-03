
class ComissionView(ModelViewSet):
	queryset = Comission.objects.all()
	serializer_class = ComissionSerializer
	permission_classes = [General, ]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)	

		comission = Comission.objects.filter(store=store)

		if request.user.has_perm('user.be_seller') and not request.user.is_superuser:
			comission = comission.filter(seller_related=request.user.seller)
		if request.user.has_perm('user.be_manager') and not request.user.is_superuser:
			comission = comission.filter(seller_related__my_manager=request.user.manager)

		serializer = self.get_serializer(comission, many=True)

		return Response(serializer.data)

