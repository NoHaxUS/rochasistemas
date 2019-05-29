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
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    pagination_class = StandardSetPagination
    permission_classes = []


    filter_mappings = {
		'store':'my_store',
	}

    @action(methods=['get'], detail=True)
    def pay_manager(self, request, pk=None):
        manager = self.get_object()
        who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username        
        manager.reset_revenue(who_reseted_revenue)
        
        messages.success(request, 'Gerentes Pagos')
