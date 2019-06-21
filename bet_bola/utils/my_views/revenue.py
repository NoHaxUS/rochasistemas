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
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.permissions import IsSuperUser
from user.models import TicketOwner, Seller, Manager
from core.models import CotationCopy, Cotation, Store
from utils.models import RewardRestriction
from utils import timezone as tzlocal
import datetime
from utils.permissions import RevenueCloseManagerPermission, RevenueManagerPermission, RevenueCloseSellerPermission, RevenueSellerPermission
from config import settings
import json


class RevenueGeneralSellerView(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.filter(payment__status=2).distinct()
    serializer_class = RevenueGeneralSellerSerializer
    permission_classes = [RevenueSellerPermission]
    pagination_class = RevenueGeneralSellerPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:                       
            return Seller.objects.none()
        queryset = self.queryset        
        return queryset.filter(my_store=user.my_store)
        
    @action(methods=['post'], detail=True, permission_classes = [RevenueCloseSellerPermission])
    def close_seller(self, request, pk=None):  
        seller = self.get_object()
        data = json.loads(request.POST.get('data'))                
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')            
        
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
    permission_classes = [RevenueManagerPermission]
    pagination_class = RevenueGeneralManagerPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:                       
            return Manager.objects.none()
        queryset = self.queryset        
        return queryset.filter(my_store=user.my_store)

    @action(methods=['post'], detail=True, permission_classes = [RevenueCloseManagerPermission])
    def close_manager(self, request, pk=None):
        manager = self.get_object()
        data = json.loads(request.POST.get('data'))    
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')                        
                   
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


class RevenueSellerView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.filter(closed_for_seller=False)
    serializer_class = RevenueSerializer  
    permission_classes = [RevenueSellerPermission]  
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
    permission_classes = [RevenueManagerPermission]
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
        