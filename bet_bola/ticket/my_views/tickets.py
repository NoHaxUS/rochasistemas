from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from ticket.serializers.ticket import TicketSerializer, CreateTicketAnonymousUserSerializer, CreateTicketLoggedUserSerializer
from ticket.paginations import TicketPagination
from ticket.permissions import CanCreateTicket, CanPayWinner, CanValidateTicket, CanCancelTicket, CanManipulateTicket
from user.permissions import IsSuperUser
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.models import TicketOwner
from core.models import CotationCopy, Cotation, Store
from utils import timezone as tzlocal
from config import settings

class TicketView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (
        StoreIsRequired, 
        IsSuperUser|CanManipulateTicket, 
        IsSuperUser|CanCreateTicket
    )
    pagination_class = TicketPagination

    filter_mappings = {
        'ticket_id':'pk',
        'store':'store',
        'ticket_status':'status',
        'created_by': 'creator__username__icontains',
        'paid_by': 'payment__who_paid__username__icontains',
        'start_creation_date':'creation_date__gte',
        'end_creation_date':'creation_date__lte',
        'payment_status':'payment__status',
        'start_payment_date': 'payment__date__gte',
        'end_payment_date': 'payment__date__lte',
        'available': 'available',
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

        ticket_reward_value = cotation_sum * serializer.validated_data['bet_value']		

        reward = Reward.objects.create()						
        
        store = Store.objects.get(id=self.request.GET['store'])
        instance = ""
        if data['success']:						
            payment = Payment.objects.create(date=None)
            creation_date = tzlocal.now()

            if self.request.user.is_authenticated:
                if self.request.user.has_perm('user.be_seller') or self.request.user.has_perm('user.be_admin'):
                    owner = TicketOwner.objects.create(first_name=serializer.validated_data['owner']['first_name'], cellphone=serializer.validated_data['owner']['cellphone'], my_store=store)
                    instance = serializer.save(creator=self.request.user, owner=owner, reward=reward, payment=payment, creation_date=creation_date,store=store)						
                owner = TicketOwner.objects.create(first_name=self.request.user.first_name, cellphone=self.request.user.cellphone, my_store=store)
                instance = serializer.save(creator=self.request.user, owner=owner, reward=reward, payment=payment, creation_date=creation_date, store=store)
            else:					
                owner = TicketOwner.objects.create(first_name=serializer.validated_data['owner']['first_name'], cellphone=serializer.validated_data['owner']['cellphone'], my_store=store)
                instance = serializer.save(owner=owner, reward=reward, payment=payment, creation_date=creation_date, store=store)


            for i_cotation in serializer.validated_data['cotations']:			
                CotationCopy(
                    original_cotation=i_cotation,
                    ticket=instance,                                        
                    price=i_cotation.price                    
                ).save()

            if self.request.user.has_perm('user.be_seller'):			
                return instance.validate_ticket(self.request.user.seller)

    @action(methods=['get'], detail=True, permission_classes=[CanPayWinner,])
    def pay_winner_punter(self, request, pk=None):		
        ticket = self.get_object()				
        response = ticket.pay_winner_punter(request.user)
        return Response(response)		



    @action(methods=['post'], detail=False, permission_classes=[])
    def validate_tickets(self, request, pk=None):
        
        response = []
        for ticket in Ticket.objects.filter(pk__in=dict(request.data)['data[]']):
            response.append(ticket.validate_ticket(request.user))
        return Response(response)


    @action(methods=['post'], detail=False, permission_classes=[])
    def cancel_tickets(self, request, pk=None):
        response = []
        for ticket in Ticket.objects.filter(pk__in=dict(request.data)['data[]']):
            response.append(ticket.cancel_ticket(request.user))
        return Response(response)


    @action(methods=['post'], detail=False, permission_classes=[])
    def toggle_availability(self, request, pk=None):
        response = []
        for ticket in Ticket.objects.filter(pk__in=dict(request.data)['data']):
            response.append(ticket.toggle_availability())
        return Response(response)
    

    @action(methods=['get'], detail=True)
    def ticket_detail(self, request, pk=None):		        
        ticket = self.get_object()

        from utils.models import TicketCustomMessage

        cotations_history = CotationCopy.objects.filter(ticket=ticket.pk)

        if cotations_history.count() > 0 and ticket.available == True:

            cotations_values = {}
            for current_cotation in cotations_history:
                cotations_values[current_cotation.original_cotation.pk] = current_cotation.price

            content = "<CENTER> -> " + settings.APP_VERBOSE_NAME.upper() + " <- <BR>"
            content += "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
            
            if ticket.seller:
                content += "<CENTER> CAMBISTA: " + ticket.seller.first_name + "<BR>"
            if ticket.owner:
                content += "<CENTER> CLIENTE: " + ticket.owner.first_name + "<BR>"
            if ticket.user:
                content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

            content += "<CENTER> APOSTA: R$" + str("%.2f" % ticket.bet_value) + "<BR>"
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
            possible_reward = cotation_sum * ticket.bet_value
            ticket = TicketSerializer(ticket)
            context = {'ticket': ticket.data,
            'cotation_sum':cotation_sum,
            'possible_reward':possible_reward,
            'print': content,'cotations_values':cotations_values, 
            'show_ticket': True, 'base_url': request.get_host()}
        else:
            context = {'show_ticket': False}

        return Response(context)		
