from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from ticket.serializers.ticket import ShowTicketSerializer, TicketSerializer, CreateTicketSerializer
from ticket.paginations import TicketPagination
from ticket.permissions import (
    CanCreateTicket, CanPayWinner, CanValidateTicket,
    CanCancelTicket, CanManipulateTicket
)
from user.permissions import IsSuperUser
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.models import TicketOwner
from core.models import CotationCopy, Cotation, Store
from utils.models import RewardRestriction
from utils import timezone as tzlocal
from config import settings
from rest_framework.permissions import IsAuthenticated
from ticket.permissions import CanToggleTicketAvailability
from ticket.logic.reward import get_reward_value
from user.permissions import IsAdminOrManagerOrSeller
import random, json, datetime


class ShowTicketView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = ShowTicketSerializer
    pagination_class = TicketPagination
    permission_classes = []

    filter_mappings = {
        'ticket_id':'ticket_id',
        'store':'store'
    }


class TicketView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = TicketPagination
    permission_classes = []


    filter_mappings = {
        'ticket_id':'ticket_id__icontains',
        'store':'store',
        'ticket_status':'status',
        'client': 'owner__first_name__icontains',
        'created_by': 'creator__username__icontains',        
        'paid_by': 'payment__who_paid__username__icontains',
        'paid_by_id': 'payment__who_paid__pk',
        'seller_cashier': 'sellercashierhistory__pk',
        'manager_cashier': 'managercashierhistory__pk',
        'start_creation_date':'creation_date__date__gte',
        'end_creation_date':'creation_date__date__lte',
        'payment_status':'payment__status',
        'start_payment_date': 'payment__date__date__gte',
        'end_payment_date': 'payment__date__date__lte',
        'available': 'available',
    }

    filter_value_transformations = {
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_payment_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_payment_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d')
    }

    def get_queryset(self):        
        user = self.request.user
        closed_for_manager = self.request.GET.get('closed_for_manager')
        tickets = Ticket.objects.filter(store=user.my_store)

        if closed_for_manager is not None:
            tickets = tickets.filter(Q(closed_in_for_manager=False) | Q(closed_out_for_manager=False, status__in=[2,4])).exclude(status__in=[5,6])

        if user.is_authenticated:
            if user.user_type == 2:   
                return tickets.filter(Q(payment__who_paid=user) | Q(creator=user)).filter(store=user.my_store).order_by('-creation_date')            
            elif user.user_type == 3:
                return tickets.filter(Q(payment__who_paid__seller__my_manager__pk=user.pk) | Q(creator=user)).filter(store=user.my_store).order_by('-creation_date')                
            return tickets.filter(store=user.my_store).order_by('-creation_date')

        return Ticket.objects.none()


    def get_ticket_id(self, store):
        alpha_num = 4
        numbers_num = 4
        alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '1234567890'
        alpha_part = ''.join((random.choice(alpha) for i in range(alpha_num)))
        num_part = ''.join((random.choice(numbers) for i in range(numbers_num)))
        ticket_id = alpha_part + '' + num_part
        
        if not store:
            raise ValueError("Store is required to create Ticket(s)")

        if Ticket.objects.filter(ticket_id=ticket_id, store=store).exists():
            self.get_ticket_id(store=store)
        else:
            return ticket_id


    def get_serializer_class(self):		
            if self.action == 'list' or self.action == 'retrieve':           
                return TicketSerializer
            return CreateTicketSerializer


    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        data = json.loads(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        create_response = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(create_response, status=status.HTTP_201_CREATED, headers=headers)


    def perform_create(self, serializer):
        store = Store.objects.get(id=self.request.GET['store'])

        for cotation in serializer.validated_data['cotations']:
            
            if cotation.game.start_date < tzlocal.now():
                return {
                    'success': False,
                    'message': "Jogo " + cotation.game.name + " já começou. Por favor o retire da aposta."
                }  
   
        payment = Payment.objects.create()
        reward = Reward.objects.create()

        ticket_id = self.get_ticket_id(store)
        
        if self.request.user.is_authenticated:
            instance = serializer.save(
                ticket_id=ticket_id,
                creator=self.request.user,
                payment=payment,
                reward=reward,
                store=store
            )
        else:
            instance = serializer.save(
                ticket_id=ticket_id, 
                payment=payment,
                reward=reward,
                store=store
            )
            
        for cotation in serializer.validated_data['cotations']:	            
            CotationCopy(
                original_cotation=cotation,
                ticket=instance,                         
                price=cotation.get_store_price(store),
                store=store
            ).save() 

        validation_message = None

        if self.request.user.has_perm('user.be_seller'):
            validation_message = instance.validate_ticket(self.request.user.seller)
        
        instance.update_ticket_reward()

        if instance.reward_has_changed():
            reward_was_changed = True
            reward_value = instance.reward.value
        else:
            reward_was_changed = False
            reward_value = 0

        if instance.max_cotation_changed():
            cotation_was_changed = True
        else:
            cotation_was_changed = False

        
        return {
            'success': True,
            'ticket_id': ticket_id,
            'display_reward_info': reward_was_changed,
            'display_cotation_info': cotation_was_changed,
            'reward_value': reward_value,
            'cotation_value': instance.cotation_sum()[1] if cotation_was_changed else 0,
            'validation_message': validation_message
        }


    @action(methods=['post'], detail=False, permission_classes=[])
    def validate_tickets(self, request, pk=None):
        ticket_ids = json.loads(request.data.get('data'))
        ticket_ids = [id.upper() for id in ticket_ids]
        response = []
        for ticket in Ticket.objects.filter(ticket_id__in=ticket_ids):
            response.append(ticket.validate_ticket(request.user))
        if not response:
            return Response([{'success':False, 'message': 'Bilhete não encontrado.'}])
        return Response(response)


    @action(methods=['post'], detail=False, permission_classes=[])
    def cancel_tickets(self, request, pk=None):
        ticket_ids = json.loads(request.data.get('data'))
        ticket_ids = [id.upper() for id in ticket_ids]
        response = []
        for ticket in Ticket.objects.filter(ticket_id__in=ticket_ids):
            response.append(ticket.cancel_ticket(request.user))
        if not response:
            return Response([{'success':False, 'message': 'Bilhete não encontrado.'}])
        return Response(response)


    @action(methods=['get'], detail=True, permission_classes=[CanToggleTicketAvailability])
    def toggle_availability(self, request, pk=None):
        ticket = self.get_object()
        ticket.toggle_availability()
        return Response({
            'success': True,
            'message': 'Alterado com Sucesso :)'
        })
