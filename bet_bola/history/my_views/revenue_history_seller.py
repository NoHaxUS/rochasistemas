from rest_framework.viewsets import ModelViewSet
from filters.mixins import FiltersMixin
from history.paginations import RevenueHistorySellerPagination
from history.models import RevenueHistorySeller
from history.permissions import BaseHistoryPermission
from history.serializers.revenue_history_seller import RevenueHistorySellerSerializer

class RevenueHistorySellerView(FiltersMixin, ModelViewSet):
    queryset = RevenueHistorySeller.objects.all()
    serializer_class = RevenueHistorySellerSerializer
    pagination_class = RevenueHistorySellerPagination
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
        if user.user_type == 4:    
            return RevenueHistorySeller.objects.all()
        return RevenueHistorySeller.objects.filter(seller__pk=self.request.user.pk)