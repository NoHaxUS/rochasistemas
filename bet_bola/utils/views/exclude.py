from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.exclude import ExcludedGameSerializer, ExcludedLeagueSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import ExcludedGame, ExcludedLeague


class ExcludedGameView(ModelViewSet):
	queryset = ExcludedGame.objects.all()
	serializer_class = ExcludedGameSerializer
	permission_classes = [StoreIsRequired, UserIsFromThisStore,]

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
	permission_classes = [StoreIsRequired, UserIsFromThisStore,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		excluded_league= ExcludedLeague.objects.filter(store=store)
		serializer = self.get_serializer(excluded_league, many=True)

		return Response(serializer.data)

