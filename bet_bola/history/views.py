from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import *
from .serializers import *


class SellerSalesHistoryView(ModelViewSet):
    queryset = SellerSalesHistory.objects.all()
    serializer_class = SellerSalesHistorySerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']     

        queryset = self.queryset.filter(store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)    


class ManagerTransactionsHistoryView(ModelViewSet):
    queryset = ManagerTransactions.objects.all()
    serializer_class = ManagerTransactionsSerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']         

        queryset = self.queryset.filter(store__id=store_id)

        if request.GET.get('manager'):            
            queryset = queryset.filter(manager__username=request.GET['manager'])
        if request.GET.get('seller'):
            queryset = queryset.filter(seller__username=request.GET['seller'])
        if request.GET.get('date'):
            queryset = queryset.filter(transaction_date__date=request.GET['date'])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class RevenueHistorySellerView(ModelViewSet):
    queryset = RevenueHistorySeller.objects.all()
    serializer_class = RevenueHistorySellerSerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']     

        queryset = self.queryset.filter(store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)    


class RevenueHistoryManagerView(ModelViewSet):
    queryset = RevenueHistoryManager.objects.all()
    serializer_class = RevenueHistoryManagerSerializer


    def list(self, request, pk=None):
        store_id = request.GET['store']     

        queryset = self.queryset.filter(store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)    


class PunterPayedHistoryView(ModelViewSet):
    queryset = PunterPayedHistory.objects.all()
    serializer_class = PunterPayedHistorySerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']     

        queryset = self.queryset.filter(store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)    

class TicketCancelationHistoryView(ModelViewSet):
    queryset = TicketCancelationHistory.objects.all()
    serializer_class = TicketCancelationHistorySerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']     

        queryset = self.queryset.filter(store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)