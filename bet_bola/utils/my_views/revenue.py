from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from ticket.serializers.cashier import RevenueSerializer, RevenueGeneralSellerSerializer, RevenueGeneralManagerSerializer
from ticket.serializers.ticket import TicketSerializer, CreateTicketSerializer
from ticket.paginations import TicketPagination, RevenueSellerPagination, RevenueManagerPagination, RevenueGeneralSellerPagination, RevenueGeneralManagerPagination
from ticket.permissions import CanCreateTicket, CanPayWinner, CanValidateTicket, CanCancelTicket, CanManipulateTicket
from user.permissions import IsSuperUser
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.models import TicketOwner, Seller, Manager
from core.models import CotationCopy, Cotation, Store
from utils.models import RewardRestriction
from utils import timezone as tzlocal
import datetime
from config import settings
import json


class RevenueGeneralSellerView(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.filter(payment__status=2).distinct()
    serializer_class = RevenueGeneralSellerSerializer
    permission_classes = ()
    pagination_class = RevenueGeneralSellerPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:                       
            return Seller.objects.none()
        queryset = self.queryset        
        return queryset.filter(my_store=user.my_store)
        

    @action(methods=['post'], detail=False)
    def close_seller(self, request, pk=None):      
        data = json.loads(request.POST.get('data'))                
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')

        if data.get('sellers_ids') == "all":
            sellers = self.queryset
        else:
            sellers = self.queryset.filter(pk=int(data.get('sellers_ids')))
                
        for seller in sellers:
            tickets = Ticket.objects.filter(payment__status=2, payment__who_paid__pk=seller.pk, closed_for_seller=False).exclude(status__in=[5,6])		
            if start_creation_date:
                tickets = tickets.filter(creation_date__gte=start_creation_date)
            if end_creation_date:
                tickets = tickets.filter(creation_date__lte=end_creation_date)
            tickets.update(closed_for_seller=True)
        
        return Response({
            'success': True,
            'message': 'Alterado com Sucesso :)'
        })
        

class RevenueGeneralManagerView(FiltersMixin, ModelViewSet):
    queryset = Manager.objects.filter(manager_assoc__payment__status=2).distinct()
    serializer_class = RevenueGeneralManagerSerializer
    permission_classes = ()
    pagination_class = RevenueGeneralManagerPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:                       
            return Manager.objects.none()
        queryset = self.queryset        
        return queryset.filter(my_store=user.my_store)

    @action(methods=['post'], detail=False)
    def close_manager(self, request, pk=None):
        data = json.loads(request.POST.get('data'))    
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')

        if data.get('managers_ids') == "all":
            managers = self.queryset
        else:
            managers = self.queryset.filter(pk=int(data.get('managers_ids')))
                
        for manager in managers:            
            tickets = Ticket.objects.filter(payment__status=2, payment__who_paid__seller__my_manager__pk=manager.pk, closed_for_manager=False).exclude(status__in=[5,6])		
            if start_creation_date:
                tickets = tickets.filter(creation_date__gte=start_creation_date)
            if end_creation_date:
                tickets = tickets.filter(creation_date__lte=end_creation_date)
            tickets.update(closed_for_manager=True)
        
        return Response({
            'success': True,
            'message': 'Alterado com Sucesso :)'
        })
    
    @action(methods=['post'], detail=False)
    def close_all_manager(self, request, pk=None):
        data = json.loads(request.POST.get('data'))
        managers_ids = [manager.pk for manager in self.queryset]
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')
                
        for id in managers_ids:            
            tickets = Ticket.objects.filter(payment__status=2, payment__who_paid__seller__my_manager__pk=int(id), closed_for_manager=False).exclude(status__in=[5,6])		
            if start_creation_date:
                tickets = tickets.filter(creation_date__gte=start_creation_date)
            if end_creation_date:
                tickets = tickets.filter(creation_date__lte=end_creation_date)
            tickets.update(closed_for_manager=True)
        
        return Response({
            'success': True,
            'message': 'Alterado com Sucesso :)'
        })
        



class RevenueSellerView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.filter(closed_for_seller=False)
    serializer_class = RevenueSerializer
    permission_classes = ()
    pagination_class = RevenueSellerPagination

    filter_mappings = {
        'ticket_id':'pk',
        'store':'store__pk',
        'ticket_status':'status',
        'created_by': 'creator__username__icontains',
        'paid_by': 'payment__who_paid__pk',        
        'start_creation_date':'creation_date__gte',
        'end_creation_date':'creation_date__lte',
        'payment_status':'payment__status',
        'start_payment_date': 'payment__date__gte',
        'end_payment_date': 'payment__date__lte',
        'available': 'available',
    }

    def get_queryset(self):
        if self.request.GET.get("start_creation_date") or self.request.GET.get("end_creation_date"):            
            return Ticket.objects.filter(store=1, payment__status=2).exclude(status__in=[5,6])    #change to request.store              
        tickets = Ticket.objects.filter(payment__status=2, closed_for_seller=False).exclude(status__in=[5,6])
        return tickets


class RevenueManagerView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.filter(closed_for_manager=False)
    serializer_class = RevenueSerializer
    permission_classes = ()
    pagination_class = RevenueManagerPagination

    filter_mappings = {
        'ticket_id':'pk',
        'store':'store__pk',
        'ticket_status':'status',
        'created_by': 'creator__username__icontains',
        'paid_by': 'payment__who_paid__username',
        'manager': 'payment__who_paid__seller__my_manager__pk',
        'start_creation_date':'creation_date__gte',
        'end_creation_date':'creation_date__lte',
        'payment_status':'payment__status',
        'start_payment_date': 'payment__date__gte',
        'end_payment_date': 'payment__date__lte',
        'available': 'available',
    }

    def list(self, request, pk=None): 
        queryset = self.get_queryset()        
        page = self.paginate_queryset(queryset)                
        serializer = self.get_serializer(page, many=True)        
                

        if page is not None:                                                
            return self.get_paginated_response(serializer.data)
                
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.GET.get("start_creation_date") or self.request.GET.get("end_creation_date"):            
            return Ticket.objects.filter(store=1,payment__status=2).exclude(status__in=[5,6])                
        tickets = Ticket.objects.filter(payment__status=2, closed_for_manager=False).exclude(status__in=[5,6])
        return tickets
        