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
from django.contrib.auth import views as auth_views
app_name = 'core'

router = DefaultRouter()
router.register(r'stores', StoreView)
router.register(r'games', GameView)
router.register(r'leagues', LeagueView)
router.register(r'locations', LocationView)
router.register(r'cotations', CotationView)
router.register(r'cotationshistory', CotationHistoryView)
router.register(r'cotationsmodified', CotationModifiedView)
router.register(r'markets', MarketView)
router.register(r'sports', SportView)



urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('able_games/',GameAbleView.as_view({'get': 'list'}), name='able_games'),
    path('able_games/<int:pk>/',GameAbleView.as_view({'get': 'retrieve'}), name='able_games_detail'),
    path('main_menu/', MainMenu.as_view()),
    path('today_games/', TodayGamesView.as_view({'get': 'list'}), name='today_games'),
    path('tomorrow_games/', TomorrowGamesView.as_view({'get': 'list'}), name='tomorrow_games'),
    path('after_tomorrow_games/', AfterTomorrowGamesView.as_view({'get': 'list'}), name='after_tomorrow_games')
]

urlpatterns += router.urls

