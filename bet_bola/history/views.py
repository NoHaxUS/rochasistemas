# from rest_framework.viewsets import ModelViewSet, ViewSet
# from rest_framework.response import Response
# from rest_framework.reverse import reverse
# from filters.mixins import FiltersMixin
# from core.permissions import StoreIsRequired, UserIsFromThisStore
# from history.permissions import BaseHistoryPermission
# from history.paginations import CancelationHistoryPagination, SellerSalesHistoryPagination
# from .models import *
# from .serializers import *



# class SellerSalesHistoryView(FiltersMixin, ModelViewSet):
#     queryset = TicketValidationHistory.objects.all()
#     serializer_class = SellerSalesHistorySerializer
#     pagination_class = SellerSalesHistoryPagination
#     permission_classes = [BaseHistoryPermission,]
    
#     filter_mappings = {
#         'start_creation_date':'date__gte',		
#         'end_creation_date':'date__lte',
#         'paid_by': 'who_validated__pk',        
# 	}    

#     def get_queryset(self):
#         return TicketValidationHistory.objects.filter(store=self.request.user.my_store)


# class ManagerTransactionsHistoryView(ModelViewSet):
#     queryset = ManagerTransactions.objects.all()
#     serializer_class = ManagerTransactionsSerializer
#     permission_classes = [StoreIsRequired, UserIsFromThisStore,]

#     def list(self, request, pk=None):
#         store_id = request.GET.get('store')

#         queryset = self.queryset.filter(store__id=store_id)
#         if request.user.has_perm('user.be_manager'):
#             queryset = queryset.filter(manager=request.user.manager)
#         if request.GET.get('manager'):            
#             queryset = queryset.filter(manager__username=request.GET['manager'])
#         if request.GET.get('seller'):
#             queryset = queryset.filter(seller__username=request.GET['seller'])
#         if request.GET.get('date'):
#             queryset = queryset.filter(transaction_date__date=request.GET['date'])
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)   

#         serializer = self.get_serializer(queryset, many=True)

#         return Response(serializer.data)





# class PunterPayedHistoryView(ModelViewSet):
#     queryset = WinnerPaymentHistory.objects.all()
#     serializer_class = PunterPayedHistorySerializer
#     permission_classes = [StoreIsRequired, UserIsFromThisStore,]

#     def list(self, request, pk=None):
#         store_id = request.GET.get('store') 

#         queryset = self.queryset.filter(store__id=store_id)

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)   

#         serializer = self.get_serializer(queryset, many=True)

#         return Response(serializer.data)    


# class TicketCancelationHistoryView(FiltersMixin, ModelViewSet):
#     queryset = TicketCancelationHistory.objects.all()
#     serializer_class = TicketCancelationHistorySerializer
#     pagination_class = CancelationHistoryPagination
#     permission_classes = [BaseHistoryPermission]
    
#     filter_mappings = {
#         'start_creation_date':'date__gte',		
#         'end_creation_date':'date__lte',
#         'paid_by': 'who_paid__pk',
#         'cancelled_by': 'who_cancelled__pk',
# 	}    

#     def get_queryset(self):
#         return TicketCancelationHistory.objects.filter(store=self.request.user.my_store)