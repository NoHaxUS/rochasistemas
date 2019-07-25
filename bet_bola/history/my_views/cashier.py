from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from history.serializers.cashier import CashierSerializer, SellersCashierSerializer, ManagersCashierSerializer
from history.paginations import SellerCashierPagination, ManagerCashierPagination, SellersCashierPagination, ManagersCashierPagination
from ticket.paginations import TicketPagination
from ticket.serializers.ticket import TicketSerializer, CreateTicketSerializer
from ticket.permissions import CanCreateTicket, CanPayWinner, CanValidateTicket, CanCancelTicket, CanManipulateTicket
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.permissions import IsSuperUser
from user.models import TicketOwner, Seller, Manager
from core.models import CotationCopy, Cotation, Store
from history.models import ManagerCashierHistory, SellerCashierHistory
from history.permissions import RevenueCloseManagerPermission, ManagerCashierPermission, RevenueCloseSellerPermission, SellerCashierPermission
from utils.models import RewardRestriction, Release
from utils import timezone as tzlocal
from config import settings
import json
import datetime
import decimal


class SellersCashier(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.filter(payment__status=2).distinct()
    serializer_class = SellersCashierSerializer
    permission_classes = [SellerCashierPermission]
    pagination_class = SellersCashierPagination

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return self.queryset.filter(pk=user.pk,my_store=self.request.user.my_store)
        elif user.user_type == 3:
            return self.queryset.filter(my_manager__pk=user.pk,my_store=self.request.user.my_store)            
        return self.queryset.filter(my_store=self.request.user.my_store)
        
    @action(methods=['post'], detail=False, permission_classes = [RevenueCloseSellerPermission])
    def close_seller(self, request, pk=None):          
        data = json.loads(request.POST.get('data'))                
        sellers_ids = data.get('sellers_ids')
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')                                                        

        for seller in Seller.objects.filter(id__in=sellers_ids):            
            serializer = SellersCashierSerializer(seller)
            data = serializer.data
            if not data['comission'] == 0 or not data['entry'] == 0 or not data['out'] == 0:
                revenue_history_seller = SellerCashierHistory(register_by=request.user, 
                seller=seller, 
                entry=decimal.Decimal(data['entry']),
                comission=decimal.Decimal(data['comission']),
                total_out=decimal.Decimal(data['total_out']),
                profit= decimal.Decimal(decimal.Decimal(data['entry']) - decimal.Decimal(data['total_out'])),
                store=request.user.my_store)           
                
                tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__pk=seller.pk,store=self.request.user.my_store, 
                    closed_for_seller=False) | Q(payment__who_paid__pk=seller.pk, status=4)).exclude(status__in=[5,6])        
                if tickets.exists():
                    if start_creation_date:
                        tickets = tickets.filter(creation_date__gte=start_creation_date)
                    if end_creation_date:
                        tickets = tickets.filter(creation_date__lte=end_creation_date)        

                    revenue_history_seller.save()        
                    revenue_history_seller.tickets_registered.set(tickets)            

                    tickets.update(closed_for_seller=True)            
                    for ticket in tickets:
                        if ticket.status == 4:
                            ticket.status = 2
                            ticket.save()

        return Response({
            'success': True,
            'message': 'Alterado com Sucesso :)'
        })
    

class ManagersCashier(FiltersMixin, ModelViewSet):
    queryset = Manager.objects.filter(manager_assoc__payment__status=2).distinct()
    serializer_class = ManagersCashierSerializer
    permission_classes = [ManagerCashierPermission]
    pagination_class = ManagersCashierPagination

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 3:
            return Manager.objects.filter(pk=user.pk)

        queryset = self.queryset        
        return queryset.filter(my_store=user.my_store)

    
    @action(methods=['post'], detail=False, permission_classes = [RevenueCloseManagerPermission])
    def close_manager(self, request, pk=None):
        data = json.loads(request.POST.get('data'))
        managers_ids = data.get('managers_ids')
        data = json.loads(request.POST.get('data'))    
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')                                

        for manager in Manager.objects.filter(id__in=managers_ids):
            serializer = ManagersCashierSerializer(manager)
            data = serializer.data
            
            if not data['comission'] == 0 or not data['entry'] == 0 or not data['out'] == 0:
                revenue_history_manager = ManagerCashierHistory(register_by=request.user, 
                manager=manager, 
                entry=decimal.Decimal(data['entry']),
                comission=decimal.Decimal(data['comission']),
                total_out=decimal.Decimal(data['total_out']),
                profit= decimal.Decimal(data['entry'] - data['total_out']),
                store=request.user.my_store)

                tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__seller__my_manager__pk=manager.pk,store=self.request.user.my_store, 
                    closed_for_manager=False) | Q(payment__who_paid__seller__my_manager__pk=manager.pk, status=4)).exclude(status__in=[5,6])        
                
                if tickets.exists():
                    if start_creation_date:
                        tickets = tickets.filter(creation_date__gte=start_creation_date)
                    if end_creation_date:
                        tickets = tickets.filter(creation_date__lte=end_creation_date)        
                    
                    revenue_history_manager.save()
                    revenue_history_manager.tickets_registered.set(tickets)

                    tickets.update(closed_for_manager=True)

        return Response({
            'success': True,
            'message': 'Alterado com Sucesso :)'
        })                


class SellerCashier(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = CashierSerializer  
    permission_classes = [SellerCashierPermission]  
    pagination_class = SellerCashierPagination

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

    filter_value_transformations = {
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_payment_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_payment_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d')
    }

    def get_queryset(self):        
        user = self.request.user
        if user.user_type == 2:   
            return Ticket.objects.filter(Q(payment__status=2, payment__who_paid=user, store=user.my_store, 
                closed_for_seller=False) | Q(payment__who_paid=user, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')
        
        elif user.user_type == 3:
            return Ticket.objects.filter(Q(payment__status=2, payment__who_paid__seller__my_manager__pk=user.pk, store=user.my_store, 
                closed_for_seller=False) | Q(payment__who_paid__seller__my_manager__pk=user.pk, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')

        return Ticket.objects.filter(Q(payment__status=2, store=user.my_store, 
                closed_for_seller=False) | Q(store=user.my_store, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')


class ManagerCashier(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = CashierSerializer
    permission_classes = [ManagerCashierPermission]
    pagination_class = ManagerCashierPagination

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

    filter_value_transformations = {
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_payment_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_payment_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d')
    }

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 3:   
            return Ticket.objects.filter(Q(payment__status=2,payment__who_paid__my_manager__pk=user.pk ,store=user.my_store, 
                closed_for_manager=False) | Q(payment__who_paid__my_manager__pk=user.pk, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')
        return Ticket.objects.filter(Q(payment__status=2, store=user.my_store, 
                closed_for_manager=False) | Q(store=user.my_store, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')
        

class RevenueView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            entries = 0
            out = 0
            total_release = 0
            comissions = 0
            total_out = 0
            user = request.user 

            if request.user.user_type == 2:
                managers = Manager.objects.none()
                sellers = Seller.objects.filter(pk=user.pk,payment__status=2, my_store=request.user.my_store).distinct()
                for release in Release.objects.filter(user=user):
                    total_release += release.value                

            elif request.user.user_type == 3:
                managers = Manager.objects.filter(pk=user.pk,manager_assoc__payment__status=2, my_store=request.user.my_store).distinct()
                sellers = Seller.objects.filter(my_manager__pk=user.pk,payment__status=2, my_store=request.user.my_store).distinct()                
                for release in Release.objects.filter(Q(user=user) | Q(user__in=user.manager.manager_assoc.all())):
                    total_release += release.value

            else:
                managers = Manager.objects.filter(manager_assoc__payment__status=2, my_store=request.user.my_store).distinct()
                sellers = Seller.objects.filter(payment__status=2, my_store=request.user.my_store).distinct()
                for release in Release.objects.filter(store=request.user.my_store):
                    total_release += release.value     

            for manager in ManagersCashierSerializer(managers, many=True, context={'request':self.request}).data:                        
                comissions += manager['comission']            
                total_out += manager['comission']

            for seller in SellersCashierSerializer(sellers, many=True, context={'request':self.request}).data:            
                entries += seller['entry']
                out += seller['out'] + seller['won_bonus']
                comissions += seller['comission']
                total_out += seller['total_out']

            profit = entries - total_out                                   
                
            data = {
                'entries': entries,
                'out': out,
                'total_release': total_release,
                'comissions': comissions,
                'total_out': total_out,
                'profit': profit
            }    

            return Response(data)
        return Response({})