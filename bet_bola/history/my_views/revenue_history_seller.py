from rest_framework.viewsets import ModelViewSet
from history.models import RevenueHistorySeller
from history.serializers.revenue_history_seller import RevenueHistorySellerSerializer

class RevenueHistorySellerView(ModelViewSet):
    queryset = RevenueHistorySeller.objects.all()
    serializer_class = RevenueHistorySellerSerializer
    # permission_classes = [StoreIsRequired, UserIsFromThisStore,]    
