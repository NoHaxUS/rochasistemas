from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket
from cashier.serializers.cashier import (
    CashierSerializer, SellersCashierSerializer, 
    ManagersCashierSerializer, ManagerEspecificCashierSerializer
)
from history.paginations import (
    SellerCashierPagination, ManagerCashierPagination, 
    SellersCashierPagination, ManagersCashierPagination
)
from user.models import Seller, Manager
from history.models import ManagerCashierHistory, SellerCashierHistory
from history.permissions import (
    CashierCloseManagerPermission, ManagerCashierPermission, 
    CashierCloseSellerPermission, SellerCashierPermission
)
from user.permissions import IsManager
import json, datetime, decimal


class SellersCashierView(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.filter(payment__status=2).distinct()
    serializer_class = SellersCashierSerializer
    permission_classes = [SellerCashierPermission]    
    pagination_class = SellersCashierPagination

    def list(self, request, pk=None):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)                                        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return self.queryset.filter(pk=user.pk,my_store=self.request.user.my_store)
        elif user.user_type == 3:
            return self.queryset.filter(my_manager__pk=user.pk,my_store=self.request.user.my_store)            
        return self.queryset.filter(my_store=self.request.user.my_store)


    @action(methods=['post'], detail=False, permission_classes = [CashierCloseSellerPermission])
    def close_seller(self, request, pk=None):          
        data = json.loads(request.POST.get('data'))                
        sellers_ids = data.get('sellers_ids')
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')                                                        

        for seller in Seller.objects.filter(id__in=sellers_ids):            
            serializer = SellersCashierSerializer(seller, context={"request":request})
            data = serializer.data              
            if not data['comission'] == 0 or not data['entry'] == 0 or not data['out'] == 0:
                revenue_history_seller = SellerCashierHistory(register_by=request.user, 
                seller=seller, 
                entry=decimal.Decimal(data['entry']),
                comission=decimal.Decimal(data['comission']),
                total_out=decimal.Decimal(data['total_out']),
                bonus_premio=decimal.Decimal(data['won_bonus']),
                profit= decimal.Decimal(decimal.Decimal(data['entry']) - decimal.Decimal(data['total_out'])),
                store=request.user.my_store)           
                
                tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__pk=seller.pk,store=self.request.user.my_store, 
                    closed_for_seller=False) | Q(payment__who_paid__pk=seller.pk, status=4)).exclude(status__in=[5,6])        
                if tickets.exists():
                    if start_creation_date:
                        start_creation_date = datetime.datetime.strptime(start_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                        tickets = tickets.filter(creation_date__date__gte=start_creation_date)
                    if end_creation_date:
                        end_creation_date = datetime.datetime.strptime(end_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                        tickets = tickets.filter(creation_date__date__lte=end_creation_date)                                       
                    
                    revenue_history_seller.save()        
                    revenue_history_seller.tickets_registered.set(tickets)            

                    tickets.update(closed_for_seller=True)            
                    for ticket in tickets:
                        if ticket.status == 4:
                            ticket.status = 2
                            ticket.save()

        return Response({
            'success': True,
            'message': 'Realizado com Sucesso :)'
        })
    

class ManagersCashierView(FiltersMixin, ModelViewSet):
    queryset = Manager.objects.filter(manager_assoc__payment__status=2).distinct()
    serializer_class = ManagersCashierSerializer
    permission_classes = [ManagerCashierPermission]
    pagination_class = ManagersCashierPagination

    def list(self, request, pk=None):        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)                        

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        user = self.request.user
        if user.user_type == 3:
            return Manager.objects.filter(pk=user.pk)

        queryset = self.queryset        
        return queryset.filter(my_store=user.my_store)

    
    @action(methods=['post'], detail=False, permission_classes = [CashierCloseManagerPermission])
    def close_manager(self, request, pk=None):
        data = json.loads(request.POST.get('data'))
        managers_ids = data.get('managers_ids')
        data = json.loads(request.POST.get('data'))    
        start_creation_date = data.get('start_creation_date')
        end_creation_date = data.get('end_creation_date')                                

        for manager in Manager.objects.filter(id__in=managers_ids):            
            serializer = ManagersCashierSerializer(manager, context={"request":request})
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
                        start_creation_date = datetime.datetime.strptime(start_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                        tickets = tickets.filter(creation_date__date__gte=start_creation_date)
                    if end_creation_date:
                        end_creation_date = datetime.datetime.strptime(end_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                        tickets = tickets.filter(creation_date__date__lte=end_creation_date)        
                    
                    revenue_history_manager.save()
                    revenue_history_manager.tickets_registered.set(tickets)

                    tickets.update(closed_for_manager=True)

        return Response({
            'success': True,
            'message': 'Realizado com Sucesso :)'
        })                


class SellerCashierView(FiltersMixin, ModelViewSet):
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
        'start_creation_date':'creation_date__date__gte',
        'end_creation_date':'creation_date__date__lte',
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

    def list(self, request, pk=None):        
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)
                
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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


class ManagerCashierView(FiltersMixin, ModelViewSet):
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
        'start_creation_date':'creation_date__date__gte',
        'end_creation_date':'creation_date__date__lte',
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

    def list(self, request, pk=None):        
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)                        
                
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 3:   
            return Ticket.objects.filter(Q(payment__status=2,payment__who_paid__seller__my_manager__pk=user.pk ,store=user.my_store, 
                closed_for_manager=False) | Q(payment__who_paid__seller__my_manager__pk=user.pk, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')
        return Ticket.objects.filter(Q(payment__status=2, store=user.my_store, 
                closed_for_manager=False) | Q(store=user.my_store, status=4)).exclude(status__in=[5,6]).order_by('-creation_date')



class ManagerEspecificCashierView(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.filter(payment__status=2).distinct()
    serializer_class = ManagerEspecificCashierSerializer
    permission_classes = [IsManager]    
    pagination_class = SellersCashierPagination

    def list(self, request, pk=None):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)                                        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        user = self.request.user        
        return self.queryset.filter(my_manager__pk=user.pk,my_store=self.request.user.my_store)
