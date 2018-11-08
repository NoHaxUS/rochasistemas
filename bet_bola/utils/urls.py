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
from . import views

app_name = 'utils'

urlpatterns = [
    path('pdf/<int:pk>/', views.PDF.as_view(), name='pdf'),
    path('validate_ticket/', views.ValidateTicket.as_view(), name='validate_ticket'),
    path('cancel_ticket/', views.CancelTicket.as_view(), name='cancel_ticket'),
    path('pay_ticket_winners/', views.PayTicketWinners.as_view(), name='pay_ticket_winners'),
]
