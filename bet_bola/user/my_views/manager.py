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
    permission_classes = []

    filter_mappings = {
		'store':'my_store',
        'login': 'username__icontains',
        'email': 'email__icontains'
    }

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')        
        data = json.loads(data)        
        serializer = self.get_serializer(data=data)               
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)                
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_is_active(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_is_active()
        return Response({
            'success': True,
            'message':  'Alterado.'
        })

    @action(methods=['post'], detail=True, permission_classes=[])
    def alter_credit(self, request, pk=None):        
        data = json.loads(request.data.get('data'))
        credit = decimal.Decimal(data.get('credit'))
        seller = self.get_object()
        seller.alter_credit(credit)
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_can_cancel_ticket(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_cancel_ticket()
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_can_sell_unlimited(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_sell_unlimited()
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_can_change_limit_time(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_change_limit_time()
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_comission_based_on_profit(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_comission_based_on_profit()
        return Response({'success': True})