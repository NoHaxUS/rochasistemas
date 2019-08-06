from rest_framework.viewsets import ModelViewSet
from filters.mixins import FiltersMixin
from history.paginations import ManagerCashierHistoryPagination
from history.permissions import BaseHistoryPermission
from history.serializers.manager_cashier import ManagerCashierHistorySerializer
from history.models import ManagerCashierHistory
import datetime
from core.cacheMixin import CacheKeyGetMixin

class ManagerCashierView(CacheKeyGetMixin, FiltersMixin, ModelViewSet):
    queryset = ManagerCashierHistory.objects.all()
    serializer_class = ManagerCashierHistorySerializer
    pagination_class = ManagerCashierHistoryPagination
    permission_classes = [BaseHistoryPermission]
    cache_group = 'manager_cashier_view_adm'
    caching_time = 60

    filter_mappings = {
		'register_by':'register_by__username__icontains',
        'entries_above':'entry__gt',
        'entries_under':'entry__lt',
        'start_creation_date':'date__date__gte',
        'end_creation_date':'date__date__lte',
    }

    filter_value_transformations = {        
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),        
    }
    
    def get_queryset(self):
        user = self.request.user       
        if user.user_type == 3:    
            return ManagerCashierHistory.objects.filter(manager__pk=user.pk).order_by('-date')
        return ManagerCashierHistory.objects.filter(store=user.my_store).order_by('-date')
        
    