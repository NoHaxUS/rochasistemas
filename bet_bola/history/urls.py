from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from history.views.credit_transactions import CreditTransactionsView
from history.views.ticket_validation import TicketValidation
from history.views.ticket_cancelation import TicketCancelation

from history.views.manager_cashier import ManagerCashierView
from history.views.seller_cashier import SellerCashierView


app_name = 'core'

router = DefaultRouter()
router.register(r'ticket_validation', TicketValidation)
router.register(r'credit_transactions', CreditTransactionsView)
router.register(r'ticket_cancelation', TicketCancelation)
router.register(r'manager_cashier_history', ManagerCashierView)
router.register(r'seller_cashier_history', SellerCashierView)

urlpatterns = router.urls
