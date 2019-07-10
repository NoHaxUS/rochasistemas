from rest_framework.viewsets import ModelViewSet
from filters.mixins import FiltersMixin
from history.paginations import RevenueHistoryManagerPagination
from history.permissions import BaseHistoryPermission
from history.serializers.revenue_history_manager import RevenueHistoryManagerSerializer
from history.models import RevenueHistoryManager

class RevenueHistoryManagerView(FiltersMixin, ModelViewSet):
    queryset = RevenueHistoryManager.objects.all()
    serializer_class = RevenueHistoryManagerSerializer
    pagination_class = RevenueHistoryManagerPagination
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
            return RevenueHistoryManager.objects.filter(manager__pk=user.pk)
        return RevenueHistoryManager.objects.filter(store=user.my_store)
        
    