from rest_framework.viewsets import ModelViewSet
from core.paginations import StandardSetPagination
from history.models import RevenueHistorySeller
from history.permissions import BaseHistoryPermission
from history.serializers.revenue_history_seller import RevenueHistorySellerSerializer

class RevenueHistorySellerView(ModelViewSet):
    queryset = RevenueHistorySeller.objects.all()
    serializer_class = RevenueHistorySellerSerializer
    pagination_class = StandardSetPagination
    permission_classes = [BaseHistoryPermission]  
