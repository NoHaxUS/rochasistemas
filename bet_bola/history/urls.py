"""bet_bola URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .views import *
from .my_views.revenue_history_manager import RevenueHistoryManagerView
from .my_views.revenue_history_seller import RevenueHistorySellerView
from .my_views.ticket_validation_history import TicketValidationHistoryView
from .my_views.ticket_cancelation_history import TicketCancelationHistoryView

app_name = 'core'

router = DefaultRouter()
router.register(r'ticket_validation_history', TicketValidationHistoryView)
# router.register(r'manager_transactions_history', ManagerTransactionsHistoryView)
# router.register(r'punter_payed_history', PunterPayedHistoryView)
router.register(r'ticket_cancelation_history', TicketCancelationHistoryView)
router.register(r'revenue_history_manager', RevenueHistoryManagerView)
router.register(r'revenue_history_seller', RevenueHistorySellerView)


urlpatterns = router.urls

