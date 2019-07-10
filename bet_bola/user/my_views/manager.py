from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib import messages
from user.models import Manager
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.permissions import IsAdmin
from user.serializers.manager import ManagerSerializer
from core.paginations import StandardSetPagination
from filters.mixins import FiltersMixin
from rest_framework.permissions import IsAuthenticated
import json
import decimal

class ManagerView(FiltersMixin, ModelViewSet):
    queryset = Manager.objects.filter(is_active=True)
    serializer_class = ManagerSerializer
    pagination_class = StandardSetPagination
    permission_classes = [IsAdmin]

    filter_mappings = {
		'store':'my_store',
        'login': 'username__icontains',
        'email': 'email__icontains'
    }
    
    def get_queryset(self):        
        user = self.request.user            
        return Manager.objects.filter(my_store=user.my_store, is_active=True)

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')      
        if not data:
            data = "{}"  
        data = json.loads(data)        
        serializer = self.get_serializer(data=data)               
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)                
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=True, permission_classes=[IsAdmin])
    def toggle_is_active(self, request, pk=None):
        manager = self.get_object()        
        manager.toggle_is_active()
        manager.username = manager.username + "(Removido)"
        count = 0
        
        while Manager.objects.filter(username=manager.username).exists():
            count+=1
            manager.username = manager.username + " " + str(count)

        manager.save()
        return Response({
            'success': True,
            'message':  'Alterado.'
        })

    @action(methods=['post'], detail=True, permission_classes=[IsAdmin])
    def alter_credit(self, request, pk=None):
        data = json.loads(request.data.get('data'))
        credit = decimal.Decimal(data.get('credit'))
        user = request.user
        manager = self.get_object()        
        
        if user.user_type == 4:            
            response = user.admin.manage_user_credit(manager, credit)
        else:
            return Response({'success': False, 'message':'Você não tem permissão para executar essa operação nesse usuário.'})
        
        return Response(response)                

    @action(methods=['get'], detail=True, permission_classes=[IsAdmin])
    def toggle_can_cancel_ticket(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_cancel_ticket()
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[IsAdmin])
    def toggle_can_sell_unlimited(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_sell_unlimited()
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[IsAdmin])
    def toggle_can_change_limit_time(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_change_limit_time()
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[IsAdmin])
    def toggle_comission_based_on_profit(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_comission_based_on_profit()
        return Response({'success': True})