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
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [    
    url(r'^$', views.Home.as_view(), name='home'),    
    url(r'^seller/home$', views.SellerHome.as_view(), name='seller_home'),
    url(r'^championship/(?P<pk>\d+)$', views.GameChampionship.as_view(), name='game_championship'),
    url(r'^bet_ticket/(?P<pk>\d+)$', views.BetTicketDetail.as_view(), name='bet_ticket_id'),
    url(r'^bet_ticket/$', views.CreateTicketView.as_view(), name='bet_ticket'),
    url(r'^bet/(?P<pk>\d+)?$', views.BetView.as_view(), name='bet'),
    url(r'^cotations/(?P<gameid>\d+)$', views.CotationsView.as_view(), name='cotations'),
    url(r'^seller/validate_ticket/$', views.ValidateTicket.as_view(), name='validate_ticket'),
    url(r'^seller/punter_payment/$', views.PunterPayment.as_view(), name='punter_payment'),
]
