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
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),    
    path('tomorrow_games/', views.TomorrowGames.as_view(), name='tomorrow_games'),    
    path('seller/home/', views.SellerHome.as_view(), name='seller_home'),
    path('championship/<int:pk>', views.GameChampionship.as_view(), name='game_championship'),
    path('bet_ticket/<int:pk>', views.BetTicketDetail.as_view(), name='bet_ticket_id'),
    path('bet_ticket/', views.CreateTicketView.as_view(), name='bet_ticket'),
    path('bet/', views.BetView.as_view(), name='bet'),
    path('bet/<str:pk>', views.BetView.as_view(), name='bet'),
    path('cotations/<int:gameid>', views.CotationsView.as_view(), name='cotations'),
    path('seller/validate_ticket/', views.ValidateTicket.as_view(), name='validate_ticket'),
    path('seller/punter_payment/', views.PunterPayment.as_view(), name='punter_payment'),
    path('config/', views.GeneralConf.as_view(), name='general_config'),
]
