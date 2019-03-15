from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import *
from .serializers import *


class SellerSalesHistoryView(ModelViewSet):
    queryset = SellerSalesHistory.objects.all()
    serializer_class = SellerSalesHistorySerializer


class ManagerTransactionsHistoryView(ModelViewSet):
    queryset = ManagerTransactions.objects.all()
    serializer_class = ManagerTransactionsSerializer


class RevenueHistorySellerView(ModelViewSet):
    queryset = RevenueHistorySeller.objects.all()
    serializer_class = RevenueHistorySellerSerializer


class RevenueHistoryManagerView(ModelViewSet):
    queryset = RevenueHistoryManager.objects.all()
    serializer_class = RevenueHistoryManagerSerializer


class PunterPayedHistoryView(ModelViewSet):
	queryset = PunterPayedHistory.objects.all()
	serializer_class = PunterPayedHistorySerializer


class TicketCancelationHistoryView(ModelViewSet):
	queryset = TicketCancelationHistory.objects.all()
	serializer_class = TicketCancelationHistorySerializer