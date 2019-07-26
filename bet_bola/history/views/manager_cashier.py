from rest_framework.viewsets import ModelViewSet
from filters.mixins import FiltersMixin
from history.paginations import ManagerCashierPagination
from history.permissions import BaseHistoryPermission
from history.serializers.manager_cashier import ManagerCashierSerializer
from history.models import ManagerCashierHistory

class ManagerCashierView(FiltersMixin, ModelViewSet):
    queryset = ManagerCashierHistory.objects.all()
    serializer_class = ManagerCashierSerializer
    pagination_class = ManagerCashierPagination
    permission_classes = [BaseHistoryPermission]

    filter_mappings = {
		'register_by':'register_by__pk',
        'entries_above':'entry__gt',
        'entries_under':'entry__lt',
        'start_creation_date':'date__gte',
        'end_creation_date':'date__lte',
    }

    def get_queryset(self):
        user = self.request.user       
        if user.user_type == 3:    
            return ManagerCashierHistory.objects.filter(manager__pk=user.pk).order_by('-date')
        return ManagerCashierHistory.objects.filter(store=user.my_store).order_by('-date')
        
    