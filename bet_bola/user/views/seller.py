from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib import messages
from user.models import Seller
from user.permissions import IsAdmin, AlterSellerPermission, IsAdminOrManager
from core.permissions import StoreIsRequired, UserIsFromThisStore
from core.paginations import StandardSetPagination
from user.serializers.seller import SellerSerializer
from user.paginations import SellerPagination
from filters.mixins import FiltersMixin
import decimal
import json

class SellerView(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.filter(is_active=True)
    serializer_class = SellerSerializer
    pagination_class = SellerPagination
    permission_classes = [IsAdminOrManager,]

    filter_mappings = {
        'login': 'username__icontains',
        'manager': 'my_manager__username__icontains',
        'email': 'email__icontains',
		'store':'my_store',
	}

    def get_queryset(self):        
        user = self.request.user
        if user.user_type == 3:            
            return Seller.objects.filter(my_manager=user.pk, my_store=user.my_store, is_active=True)
        return Seller.objects.filter(my_store=user.my_store, is_active=True)

    def create(self, request, *args, **kwargs):
        data = json.loads(request.data.get('data')) if request.data.get('data') else request.data
        data = {} if not data else data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=True, permission_classes=[AlterSellerPermission])
    def toggle_is_active(self, request, pk=None):
        seller = self.get_object()        
        seller.toggle_is_active()
        seller.username = seller.username + "_removido"
        count = 0
        
        while Seller.objects.filter(username=seller.username).exists():
            count+=1
            seller.username = seller.username + "_" + str(count)

        seller.save()
        return Response({
            'success': True,
            'message':  'Alterado.'
        })        

    @action(methods=['post'], detail=True, permission_classes=[AlterSellerPermission])
    def alter_credit(self, request, pk=None):
        data = request.data.get('data')
        data = json.loads(data)
        user = request.user
        credit =  decimal.Decimal(data['credit'])
        seller = self.get_object()
        
        if user.user_type == 3 and user.manager == seller.my_manager:            
            response = user.manager.manage_seller_credit(seller, credit)
        elif user.user_type == 4:            
            response = user.admin.manage_user_credit(seller, credit)
        else:
            return Response({'success': False, 'message':'Você não tem permissão para executar essa operação nesse usuário.'})
        
        return Response(response)

    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_can_sell_unlimited(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_sell_unlimited()
        return Response({'success': True})

    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_can_cancel_ticket(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_can_cancel_ticket()
        return Response({'success': True})



