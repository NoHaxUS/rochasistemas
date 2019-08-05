from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from ticket.views.tickets import TicketView, ShowTicketView
from ticket.views.rewards import RewardView
from ticket.views.payments import PaymentView

app_name = 'core'

router = DefaultRouter()
router.register(r'tickets', TicketView)
router.register(r'show_ticket', ShowTicketView)
#router.register(r'rewards', RewardView)
#router.register(r'payments', PaymentView)

urlpatterns = router.urls
