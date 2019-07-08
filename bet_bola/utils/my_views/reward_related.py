from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from utils.serializers.reward_related import RewardRelatedSerializer
from user.permissions import IsAdmin
from utils.models import RewardRestriction
import json

class RewardRelatedView(ModelViewSet):
	queryset = RewardRestriction.objects.all().order_by('bet_value')
	serializer_class = RewardRelatedSerializer
	permission_classes = [IsAdmin,]


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


	@action(methods=['post'], detail=False, permission_classes=[])
	def check_reward(self, request, pk=None):		
		content = json.loads(request.data['ticket'])
		ticket_value = json.loads(request.data['ticket_value'])
		cotation_total = 1
		for cotation in content:
			cotation_total = cotation_total * float(content[cotation]['cotation_value'])
			
		reward_value = cotation_total * ticket_value		
		rewards_restrictions = RewardRestriction.objects.filter(bet_value__lte = ticket_value, max_reward_value__lt=reward_value, store__pk=request.GET.get('store')).order_by('bet_value')
		
		if rewards_restrictions.exists():			
			reward_message = "Valor maximo do premio para apostas menor ou igual a "+ str(ticket_value) +"R$ é " + str(rewards_restrictions.last().max_reward_value) + "R$, se deseja confirmar a aposta, clique em ok."			
			return Response({"warning":reward_message})
		return Response({})		