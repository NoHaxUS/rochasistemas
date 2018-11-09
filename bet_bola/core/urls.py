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
    path('after_tomorrow/', views.AfterTomorrowGames.as_view(), name='after_tomorrow_games'),
    path('tomorrow_games/', views.TomorrowGames.as_view(), name='core_tomorrow_games'),
    path('league/<int:pk>/', views.GameLeague.as_view(), name='core_championship_get'),
    path('ticket/<int:pk>/', views.TicketDetail.as_view(), name='core_ticket_get'),
    path('ticket/', views.CreateTicketView.as_view(), name='core_ticket_post'),
    path('bet/', views.BetView.as_view(), name='core_bet_get'),
    path('bet/<str:pk>/', views.BetView.as_view(), name='core_bet_post'),
    path('cotations/<int:gameid>/', views.CotationsView.as_view(), name='core_cotations_get'),
    path('app/', views.AppDownload.as_view(), name='core_app_download'),
    path('rules/', views.RulesView.as_view(), name='core_rules'),
]
