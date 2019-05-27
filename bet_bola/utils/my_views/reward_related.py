from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.reward_related import RewardRelatedSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import RewardRestriction

class RewardRelatedView(ModelViewSet):
	queryset = RewardRestriction.objects.all().order_by('bet_value')
	serializer_class = RewardRelatedSerializer
	permission_classes = [StoreIsRequired, UserIsFromThisStore,]


	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rewards_related= RewardRestriction.objects.filter(store=store)
		serializer = self.get_serializer(rewards_related, many=True)

		return Response(serializer.data)
	
	def perform_create(self, serializer):		
		store = self.request.user.my_store
		max_reward_value = serializer.validated_data['max_reward_value']
		bet_value = serializer.validated_data['bet_value']		
		if RewardRestriction.objects.filter(store=store, bet_value=bet_value).exists():
			reward_restriction = RewardRestriction.objects.get(store=store, bet_value=bet_value)
			reward_restriction.max_reward_value = max_reward_value			
			reward_restriction.save()
			return reward_restriction		
		return RewardRestriction.objects.create(store=store, max_reward_value=max_reward_value, bet_value=bet_value)


