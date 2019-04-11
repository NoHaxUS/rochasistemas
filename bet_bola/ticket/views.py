from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from core.models import Cotation, CotationHistory, Store
from utils import timezone as tzlocal
from .permissions import CreateBet, PayWinnerPermission
from .models import *
from .serializers import *


class TicketView(ModelViewSet):
	queryset = Ticket.objects.all()
	serializer_class = TicketSerializer
	permission_classes = [CreateBet,]

	def list(self, request, pk=None):
		store_id = request.GET.get('store')     

		queryset = self.queryset.filter(store__id=store_id)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)   
		
		serializer = self.get_serializer(queryset, many=True)

		return Response(serializer.data)

	def retrieve(self, request, pk=None):
		store_id = request.GET['store']     

		queryset = Ticket.objects.filter(store__id=store_id)
		user = get_object_or_404(queryset, pk=pk)
		serializer = self.get_serializer(user)
		return Response(serializer.data)

	def get_serializer_class(self):		
			if self.action == 'list':           
				return TicketSerializer
			elif self.action == 'retrieve':
				return TicketSerializer		
			if self.request.user.is_authenticated:				
				return CreateTicketLoggedUserSerializer
			return CreateTicketAnonymousUserSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		message = self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		if message:		
			data = [serializer.data,{'Validation':message}]		
			return Response(data, status=status.HTTP_201_CREATED, headers=headers)		
			
		data = serializer.data
		return Response(data, status=status.HTTP_201_CREATED, headers=headers)		

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
		
		store = Store.objects.get(id=self.request.GET['store'])
		instance = ""
		if data['success']:						
			payment = Payment.objects.create(payment_date=None)
			creation_date = tzlocal.now()

			if self.request.user.is_authenticated:
				if self.request.user.has_perm('user.be_seller'):
					normal_user = NormalUser.objects.create(first_name=serializer.validated_data['normal_user']['first_name'], cellphone=serializer.validated_data['normal_user']['cellphone'], my_store=store)
					instance = serializer.save(seller=self.request.user,normal_user=normal_user, reward=reward, payment=payment, creation_date=creation_date,store=store)						
				instance = serializer.save(user=self.request.user, reward=reward, payment=payment, creation_date=creation_date, store=store)
			else:					
				normal_user = NormalUser.objects.create(first_name=serializer.validated_data['normal_user']['first_name'], cellphone=serializer.validated_data['normal_user']['cellphone'], my_store=store)
				instance = serializer.save(normal_user=normal_user, reward=reward, payment=payment, creation_date=creation_date, store=store)


			for i_cotation in serializer.validated_data['cotations']:			
				CotationHistory(
					original_cotation=i_cotation,
					ticket=instance,
					name=i_cotation.name,
					start_price=i_cotation.start_price,
					price=i_cotation.price,
					game=i_cotation.game,								
					market=i_cotation.market						
				).save()

			if self.request.user.has_perm('user.be_seller'):			
				return instance.validate_ticket(self.request.user.seller)

	@action(methods=['get'], detail=True, permission_classes=[PayWinnerPermission,])
	def pay_winner_punter(self, request, pk=None):		
		ticket = self.get_object()				
		response = ticket.pay_winner_punter(request.user)
		return Response(response)		

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

	@action(methods=['get'], detail=True)
	def validar_ticket(self, request, pk=None):
		if request.user.has_perm('user.be_seller'):
			if not str(request.GET['store']):
				return Response({"failed":"Entrada da banca não inserida"})						
			if str(request.user.seller.my_store.id) != str(request.GET['store']):
				return Response({"failed":"Usuário não é vendedor desta banca"})						
			ticket = self.get_object()			
			return Response(ticket.validate_ticket(request.user))
		return Response({"failed":"Usuário não é vendedor"})

	@action(methods=['get'], detail=True)
	def cancel_ticket(self, request, pk=None):		
		ticket = self.get_object()
		if str(request.user.seller.my_store.id) != str(request.GET['store']):
				return Response({"failed":"Usuário não é vendedor desta banca"})						
		return Response(ticket.cancel_ticket(request.user.seller))

	@action(methods=['get'], detail=True)
	def ticket_detail(self, request, pk=None):		        
		ticket = self.get_object()

		from utils.models import TicketCustomMessage

		cotations_history = CotationHistory.objects.filter(ticket=ticket.pk)

		if cotations_history.count() > 0 and ticket.visible == True:

		    cotations_values = {}
		    for current_cotation in cotations_history:
		        cotations_values[current_cotation.original_cotation.pk] = current_cotation.price

		    content = "<CENTER> -> " + settings.APP_VERBOSE_NAME.upper() + " <- <BR>"
		    content += "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
		    
		    if ticket.seller:
		        content += "<CENTER> CAMBISTA: " + ticket.seller.first_name + "<BR>"
		    if ticket.normal_user:
		        content += "<CENTER> CLIENTE: " + ticket.normal_user.first_name + "<BR>"
		    if ticket.user:
		        content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

		    content += "<CENTER> APOSTA: R$" + str("%.2f" % ticket.value) + "<BR>"
		    content += "<CENTER> COTA TOTAL: " + str("%.2f" % ticket.cotation_sum() ) + "<BR>"
		    if ticket.reward:
		        content += "<CENTER> GANHO POSSIVEL: R$" + str("%.2f" % ticket.reward.real_value) + "<BR>"
		    if ticket.payment:
		        content +=  "<CENTER> STATUS: " + ticket.payment.status_payment + "<BR>"
		    content += "<CENTER> DATA: " + ticket.creation_date.strftime('%d/%m/%Y %H:%M')
		    content += "<BR><BR>"
		    
		    content += "<LEFT> APOSTAS <BR>"
		    content += "<LEFT>-------------------------------> <BR>"

		    for cotation in ticket.cotations.all():
		        content += "<LEFT>" + cotation.game.name + "<BR>"
		        content += "<LEFT>" + cotation.game.start_date.strftime('%d/%m/%Y %H:%M') + "<BR>"
		        if cotation.market:
		            content += "<LEFT>"+ cotation.market.name + "<BR>"

		        base_line = cotation.base_line if cotation.base_line else ''
		        content += "<LEFT>" + cotation.name + ' ' + base_line + " --> " + str("%.2f" % cotations_values[cotation.pk]) + "<BR>"

		        content += "<RIGHT> Status: " +  cotation.get_settlement_display_modified() + "<BR>"
		        
		        content += "<CENTER>-------------------------------> <BR>"
		    content += "<CENTER> "+ settings.APP_VERBOSE_NAME + "<BR>"

		    if TicketCustomMessage.objects.first():            
		        phrases = TicketCustomMessage.objects.first().text.replace("\r","").split("\n")

		        for phrase in phrases:                
		            content += "<CENTER> " + phrase + "<BR>"

		    content += "#Intent;scheme=quickprinter;package=pe.diegoveloper.printerserverapp;end;"                
		    cotation_sum = ticket.cotation_sum()
		    possible_reward = cotation_sum * ticket.value
		    ticket = TicketSerializer(ticket)
		    context = {'ticket': ticket.data,
		    'cotation_sum':cotation_sum,
		    'possible_reward':possible_reward,
		    'print': content,'cotations_values':cotations_values, 
		    'show_ticket': True, 'base_url': request.get_host()}
		else:
		    context = {'show_ticket': False}

		return Response(context)		


class RewardView(ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer


class PaymentView(ModelViewSet):
	queryset = Payment.objects.all()
	serializer_class = PaymentSerializer
