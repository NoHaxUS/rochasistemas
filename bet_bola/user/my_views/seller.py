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




