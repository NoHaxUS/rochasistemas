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
    path('', views.TodayGames.as_view(), name='core_home'),
    path('all_games/', views.AllGames.as_view(), name='core_all_games'),
    path('tomorrow_games/', views.TomorrowGames.as_view(), name='core_tomorrow_games'),
    path('championship/<int:pk>/', views.GameChampionship.as_view(), name='core_championship_get'),
    path('ticket/<int:pk>/', views.TicketDetail.as_view(), name='core_ticket_get'),
    path('ticket/', views.CreateTicketView.as_view(), name='core_ticket_post'),
    path('bet/', views.BetView.as_view(), name='core_bet_get'),
    path('bet/<str:pk>/', views.BetView.as_view(), name='core_bet_post'),
    path('cotations/<int:gameid>/', views.CotationsView.as_view(), name='core_cotations_get'),
    path('config/', views.GeneralConf.as_view(), name='core_config'),
    path('reset_revenue/', views.ResetSellerRevenue.as_view(), name='core_reset_seller_revenue'),
    path('app/', views.AppDownload.as_view(), name='core_app_download'),
]
