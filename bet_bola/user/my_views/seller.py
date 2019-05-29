from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib import messages
from user.models import Seller
from user.permissions import IsAdmin
from core.permissions import StoreIsRequired, UserIsFromThisStore
from core.paginations import StandardSetPagination
from user.serializers.seller import SellerSerializer
from filters.mixins import FiltersMixin

class SellerView(FiltersMixin, ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    pagination_class = StandardSetPagination

    filter_mappings = {
        'login': 'username__icontains',
        'email': 'email__icontains',
		'store':'my_store',
	}


    @action(methods=['post'], detail=True, permission_classes=[])
    def alter_credit(self, request, pk=None):
        
        print(request.data)
        credit =  int(request.data['credit'])
        seller = self.get_object()
        seller.alter_credit(credit)
        return Response({'success': True})

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


    @action(methods=['get'], detail=True)
    def pay_seller(self, request, pk=None):
        seller = self.get_object()
        who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username
        seller.reset_revenue(who_reseted_revenue)

        return Response({'success':'Cambista Pago'})

    @action(methods=['post'], detail=True)
    def add_credit(self, request, pk=None):
        try:
            valor = request.data['value']
        except KeyError:
            return Response({"Error": "Entrada invalida. Dica:{'value':'?'}"})

        instance = self.get_object()        
        if request.user.has_perm('user.be_manager'):            
            if request.user.manager.my_store.pk != instance.my_store.pk:
                return Response({'failed':'Gerente não pertence a mesma loja que o vendedor em questão'})
            instance.credit_limit += valor
            credit_transation = request.user.manager.manage_credit(instance)
            return Response(credit_transation)

