class ExcludedGameView(ModelViewSet):
	queryset = ExcludedGame.objects.all()
	serializer_class = ExcludedGameSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		excluded_game= ExcludedGame.objects.filter(store=store)
		serializer = self.get_serializer(excluded_game, many=True)

		return Response(serializer.data)


class ExcludedLeagueView(ModelViewSet):
	queryset = ExcludedLeague.objects.all()
	serializer_class = ExcludedLeagueSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		excluded_league= ExcludedLeague.objects.filter(store=store)
		serializer = self.get_serializer(excluded_league, many=True)

		return Response(serializer.data)

