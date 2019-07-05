from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .my_views.manager_transactions_history import ManagerTransactionsHistoryView
from .my_views.revenue_history_manager import RevenueHistoryManagerView
from .my_views.revenue_history_seller import RevenueHistorySellerView
from .my_views.ticket_validation_history import TicketValidationHistoryView
from .my_views.ticket_cancelation_history import TicketCancelationHistoryView
from .my_views.revenue import RevenueSellerView, RevenueManagerView, RevenueGeneralSellerView, RevenueGeneralManagerView,RevenueView

app_name = 'core'

router = DefaultRouter()
router.register(r'ticket_validation_history', TicketValidationHistoryView)
router.register(r'manager_transactions_history', ManagerTransactionsHistoryView)
# router.register(r'punter_payed_history', PunterPayedHistoryView)
router.register(r'ticket_cancelation_history', TicketCancelationHistoryView)
router.register(r'revenue_history_manager', RevenueHistoryManagerView)
router.register(r'revenue_history_seller', RevenueHistorySellerView)
router.register(r'revenue_general_seller', RevenueGeneralSellerView)
router.register(r'revenue_general_manager', RevenueGeneralManagerView)

urlpatterns = [
    path('revenue_seller/', RevenueSellerView.as_view({'get': 'list'}), name='seller_general_info'),    
    path('revenue_manager/', RevenueManagerView.as_view({'get': 'list'}), name='manager_info'),    
    path('revenue/', RevenueView.as_view(), name='manager_info')
]

urlpatterns += router.urls
