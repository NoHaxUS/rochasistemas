from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import *
from .serializers import *
from .permissions import General


class SellerSalesHistoryView(ModelViewSet):
    queryset = SellerSalesHistory.objects.all()
    serializer_class = SellerSalesHistorySerializer
    permission_classes = [General,]

    def list(self, request, pk=None):
        store_id = request.GET['store']     

        queryset = self.queryset.filter(store__id=store_id)
        if request.GET.get('seller'):
            queryset = queryset.filter(seller__pk=request.GET.get('seller'))
        if request.GET.get('ticket'):
            queryset = queryset.filter(bet_ticket__pk=request.GET.get('ticket'))        
        if request.GET.get('date'):
            queryset = queryset.filter(sell_date__date=request.GET.get('date'))        
        if request.user.has_perm('user.be_seller') and not request.user.is_superuser:
            queryset = queryset.filter(seller=request.user.seller)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)    


class ManagerTransactionsHistoryView(ModelViewSet):
    queryset = ManagerTransactions.objects.all()
    serializer_class = ManagerTransactionsSerializer
    permission_classes = [General,]

    def list(self, request, pk=None):
        store_id = request.GET.get('store')

        queryset = self.queryset.filter(store__id=store_id)
        if request.user.has_perm('user.be_manager'):
            queryset = queryset.filter(manager=request.user.manager)
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
        store_id = request.GET.get('store')
        
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
        store_id = request.GET.get('store')

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
        store_id = request.GET.get('store') 

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
    permission_classes = [General,]

    def list(self, request, pk=None):
        store_id = request.GET.get('store')

        queryset = self.queryset.filter(store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)