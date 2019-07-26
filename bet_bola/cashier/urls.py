from django.urls import path, include
from rest_framework.routers import DefaultRouter
from cashier.views.cashier import (
    SellerCashier, ManagerCashier, 
    SellersCashier, ManagersCashier
)
from cashier.views.general_cashier import  GeneralCashier

app_name = 'cashier'

router = DefaultRouter()
router.register(r'sellers_cashier', SellersCashier)
router.register(r'managers_cashier', ManagersCashier)

urlpatterns = [
    path('seller_cashier/', SellerCashier.as_view({'get': 'list'}), name='seller_cashier'),    
    path('manager_cashier', ManagerCashier.as_view({'get': 'list'}), name='manager_cashier'),    
    path('general_cashier/', GeneralCashier.as_view(), name='general_cashier')
]

urlpatterns += router.urls

