from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from core.models import Cotation, CotationHistory
from utils import timezone as tzlocal
from .models import *
from .serializers import *


class TicketView(ModelViewSet):
	queryset = Ticket.objects.all()
	serializer_class = TicketSerializer

	def get_serializer_class(self):
		if self.action == 'list':           
			return TicketSerializer
		elif self.action == 'retrieve':
			return TicketSerializer
		return CreateTicketSerializer

	def perform_create(self, serializer):
		data = {
			'success': True
		}				

		cotation_sum = 1						
		for cotation in serializer.validated_data['cotations']:								
			try:																						
				cotation_sum *= cotation.price				
			except Cotation.DoesNotExist:
				pass	

		ticket_reward_value = cotation_sum * serializer.validated_data['value']
		reward = Reward.objects.create(reward_status='Aguardando Resultados')						
			
		if data['success']:						
			payment = Payment.objects.create(payment_date=None)
			creation_date = tzlocal.now()
			if self.request.user.is_authenticated:				
				user = self.request.user				
				serializer.save(user=user, reward=reward, payment=payment, creation_date=creation_date)	
			else:					
				normal_user = NormalUser.objects.create(first_name=serializer.validated_data['normal_user']['first_name'], cellphone=serializer.validated_data['normal_user']['cellphone'], my_store=serializer.validated_data['normal_user']['my_store'])						
				serializer.save(normal_user=normal_user, reward=reward, payment=payment, creation_date=creation_date)	

		for i_cotation in serializer.validated_data['cotations']:			
			CotationHistory(
				original_cotation=i_cotation,
				ticket=Ticket.objects.last(),
				name=i_cotation.name,
				start_price=i_cotation.start_price,
				price=i_cotation.price,
				game=i_cotation.game,								
				market=i_cotation.market,				
			).save()

	@action(methods=['get'], detail=True)
	def pay_winner_punter(self, request, pk=None):
		if request.user.has_perm('user.be_seller'):
			ticket = self.get_object()	
			response = ticket.pay_winner_punter(request.user)
			return Response(response)
		return Response({"failed":"Usuário não é vendedor"})

	@action(methods=['post'], detail=False)
	def validar_tickets(self, request, pk=None):
		if request.user.has_perm('user.be_seller'):		
			pre_id_lista = []
			
			try:
				pre_id_lista = [data["id"] for data in request.data]
			except KeyError:
				return Response({"Error": "Entrada invalida. Dica:[{'id':'?'},{'id':'?'}]"})

			id_list = []
			response = {}
			for ticket in Ticket.objects.filter(pk__in=pre_id_lista):			
				id_list.append(ticket.pk)
				response["ticket " + str(ticket.pk)] = ticket.validate_ticket(request.user)["message"]			

			warnning_id = list(set(pre_id_lista)-set(id_list))
			count=0
			for id in warnning_id:
				count += 1
				response["warning " + str(count)] = "ticket " + str(id) + " não existe" 
			return Response(response)

		return Response({"failed":"Usuário não é vendedor"})


class RewardView(ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer


class PaymentView(ModelViewSet):
	queryset = Payment.objects.all()
	serializer_class = PaymentSerializer
