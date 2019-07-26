from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .my_views.manager_transactions_history import ManagerTransactionsHistoryView
from .my_views.manager_cashier_history import ManagerCashierHistoryView
from .my_views.seller_cashier_history import SellerCashierHistoryView
from .my_views.ticket_validation_history import TicketValidationHistoryView
from .my_views.ticket_cancelation_history import TicketCancelationHistoryView
from .my_views.cashier import SellerCashier, ManagerCashier, SellersCashier, ManagersCashier,RevenueView

app_name = 'core'

router = DefaultRouter()
router.register(r'ticket_validation_history', TicketValidationHistoryView)
router.register(r'manager_transactions_history', ManagerTransactionsHistoryView)
# router.register(r'punter_payed_history', PunterPayedHistoryView)
router.register(r'ticket_cancelation_history', TicketCancelationHistoryView)
router.register(r'revenue_history_manager', ManagerCashierHistoryView)
router.register(r'revenue_history_seller', SellerCashierHistoryView)
router.register(r'revenue_general_seller', SellersCashier)
router.register(r'revenue_general_manager', ManagersCashier)

urlpatterns = [
    path('revenue_seller/', SellerCashier.as_view({'get': 'list'}), name='seller_general_info'),    
    path('revenue_manager/', ManagerCashier.as_view({'get': 'list'}), name='manager_info'),    
    path('revenue/', RevenueView.as_view(), name='manager_info')
]

urlpatterns += router.urls
