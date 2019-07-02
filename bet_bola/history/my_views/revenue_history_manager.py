from rest_framework.viewsets import ModelViewSet
from history.paginations import RevenueHistoryManagerPagination
from history.permissions import BaseHistoryPermission
from history.serializers.revenue_history_manager import RevenueHistoryManagerSerializer
from history.models import RevenueHistoryManager

class RevenueHistoryManagerView(ModelViewSet):
    queryset = RevenueHistoryManager.objects.all()
    serializer_class = RevenueHistoryManagerSerializer
    pagination_class = RevenueHistoryManagerPagination
    permission_classes = [BaseHistoryPermission]
    