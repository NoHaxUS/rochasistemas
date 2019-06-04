from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.contrib import messages
from rest_framework.response import Response
from user.models import Manager
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.permissions import IsAdmin
from user.serializers.manager import ManagerSerializer
from core.paginations import StandardSetPagination
from filters.mixins import FiltersMixin

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

    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_is_active(self, request, pk=None):
        seller = self.get_object()
        seller.toggle_is_active()
        return Response({'success': True})

    @action(methods=['post'], detail=True, permission_classes=[])
    def alter_credit(self, request, pk=None):
        credit =  int(request.data['credit'])
        seller = self.get_object()
        seller.alter_credit(credit)
        return Response({'success': True})


    @action(methods=['get'], detail=True, permission_classes=[])
    def toggle_can_cancel_ticket(self, request, pk=None):
        print(request.headers['store'])
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