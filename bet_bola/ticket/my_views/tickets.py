from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from ticket.serializers.ticket import TicketSerializer, CreateTicketAnonymousUserSerializer, CreateTicketLoggedUserSerializer
from ticket.paginations import TicketPagination
from ticket.permissions import CreateBet, PayWinnerPermission, ValidateTicketPermission, CancelarTicketPermission
from core.permissions import StoreIsRequired, UserIsNotFromThisStore
from user.models import AnonymousUser
from core.models import CotationCopy, Cotation, Store
from utils import timezone as tzlocal
from config import settings

class TicketView(FiltersMixin, ModelViewSet):
	queryset = Ticket.objects.all()
	serializer_class = TicketSerializer
	permission_classes = [UserIsNotFromThisStore ,StoreIsRequired ,CreateBet]
	pagination_class = TicketPagination

	filter_mappings = {
		'ticket_id':'pk',
		'store':'store',
		'ticket_status':'status',
		'paid_by': 'payment__who_paid',
		'start_creation_date':'creation_date__gte',
		'end_creation_date':'creation_date__lte',
		'payment_status':'payment__status',
		'start_date': 'payment__date__gte',
		'end_date': 'payment__date__lte'
	}

	def get_serializer_class(self):		
			if self.action == 'list' or self.action == 'retrieve':           
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
			
		data = [serializer.data]
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

		reward = Reward.objects.create()						
		
		store = Store.objects.get(id=self.request.GET['store'])
		instance = ""
		if data['success']:						
			payment = Payment.objects.create(date=None)
			creation_date = tzlocal.now()

			if self.request.user.is_authenticated:
				if self.request.user.has_perm('user.be_seller'):
					normal_user = AnonymousUser.objects.create(first_name=serializer.validated_data['normal_user']['first_name'], cellphone=serializer.validated_data['normal_user']['cellphone'], my_store=store)
					instance = serializer.save(seller=self.request.user,normal_user=normal_user, reward=reward, payment=payment, creation_date=creation_date,store=store)						
				instance = serializer.save(user=self.request.user, reward=reward, payment=payment, creation_date=creation_date, store=store)
			else:					
				normal_user = AnonymousUser.objects.create(first_name=serializer.validated_data['normal_user']['first_name'], cellphone=serializer.validated_data['normal_user']['cellphone'], my_store=store)
				instance = serializer.save(normal_user=normal_user, reward=reward, payment=payment, creation_date=creation_date, store=store)


			for i_cotation in serializer.validated_data['cotations']:			
				CotationCopy(
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


	@action(methods=['post'], detail=False, permission_classes=[ValidateTicketPermission, StoreIsRequired, UserIsNotFromThisStore])
	def validate_tickets(self, request, pk=None):		
		pre_id_list = []

		try:				
			pre_id_list = request.data
		except KeyError:
			return Response({'Error': 'Entrada invalida. Dica:[id_1,id_2]'})

		id_list = []
		response = []
		for ticket in Ticket.objects.filter(pk__in=pre_id_list):			
			id_list.append(ticket.pk)
			response.append(ticket.validate_ticket(request.user))

		print(pre_id_list, id_list)
		warnning_id = list(set(pre_id_list)-set(id_list))
		count=0
		for id in warnning_id:
			count += 1
			response.append({"success":False,"message": "ticket " + str(id) + " não existe"})
		return Response(response)


	@action(methods=['post'], detail=False, permission_classes=[])
	def toggle_visibilities(self, request, pk=None):
		
		pre_id_list = []
		try:
			received_data = dict(request.data)
			pre_id_list = [int(item) for item in received_data['data']]
			
		except KeyError:
			return Response({'Error': 'Entrada invalida. Dica:[id_1,id_2]'})

		id_list = []
		response = []
		for ticket in Ticket.objects.filter(pk__in=pre_id_list):			
			id_list.append(ticket.pk)
			ticket.visible = not ticket.visible
			ticket.save()
			response.append({"success": True, "message": "Visibilidade do ticket " + str(ticket.pk) + " foi alterada para " + str(ticket.visible) + " com sucesso"})

		warnning_id = list(set(pre_id_list)-set(id_list))
		count=0
		for id in warnning_id:
			count += 1
			response.append({"success":False,"message": "ticket " + str(id) + " não existe"})
		return Response(response)

		return Response([{"success":False,"message":"Usuário não tem permissão pra executar essa operação"}])
		

	@action(methods=['post'], detail=False, permission_classes=[ValidateTicketPermission, StoreIsRequired, UserIsNotFromThisStore])
	def cancel_tickets(self, request, pk=None):	
		pre_id_list = []

		try:				
			pre_id_list = request.data
		except KeyError:
			return Response({'Error': 'Entrada invalida. Dica:[id_1,id_2]'})

		id_list = []
		response = []
		for ticket in Ticket.objects.filter(pk__in=pre_id_list):			
			id_list.append(ticket.pk)
			response.append(ticket.cancel_ticket(request.user.seller))
		
		warnning_id = list(set(pre_id_list)-set(id_list))
		count=0
		for id in warnning_id:
			count += 1
			response.append({"success":False,"message": "ticket " + str(id) + " não existe"})
		return Response(response)				

	@action(methods=['get'], detail=True)
	def ticket_detail(self, request, pk=None):		        
		ticket = self.get_object()

		from utils.models import TicketCustomMessage

		cotations_history = CotationCopy.objects.filter(ticket=ticket.pk)

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
		        content +=  "<CENTER> STATUS: " + ticket.payment.status + "<BR>"
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
