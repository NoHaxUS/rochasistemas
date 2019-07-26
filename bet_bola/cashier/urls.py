from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cashier.views.cashier import (
    SellerCashierView, ManagerCashierView, 
    SellersCashierView, ManagersCashierView
)
from cashier.views.general_cashier import  GeneralCashier

app_name = 'cashier'

router = DefaultRouter()
router.register(r'sellers_cashier', SellersCashierView)
router.register(r'managers_cashier', ManagersCashierView)

urlpatterns = [
    path('seller_cashier/', SellerCashierView.as_view({'get': 'list'}), name='seller_cashier'),    
    path('manager_cashier', ManagerCashierView.as_view({'get': 'list'}), name='manager_cashier'),    
    path('general_cashier/', GeneralCashier.as_view(), name='general_cashier')
]

urlpatterns += router.urls

