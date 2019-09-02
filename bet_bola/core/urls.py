from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from core.views.games import (
    TodayGamesAdmin, GamesTable, GamesTomorrowAdmin, 
    GamesAfterTomorrowAdmin, SearchGamesView, TodayGamesView, 
    TomorrowGamesView, AfterTomorrowGamesView
)
from core.views.sports import SportView
from core.views.stores import StoreView
from core.views.locations import LocationView, LocationModifiedView
from core.views.leagues import LeagueAdminView, LeagueModifiedView
from core.views.cotations import CotationView, CotationCopyView, CotationModifiedView
from core.views.markets import MarketView, MarketCotationView
from core.views.general import APIRootView, MainMenu, ChangePassword


app_name = 'core'

router = DefaultRouter()
router.register(r'stores', StoreView)
router.register(r'leagues', LeagueAdminView)
router.register(r'locations', LocationView)
router.register(r'cotations', CotationView)
router.register(r'cotationshistory', CotationCopyView)
router.register(r'cotationsmodified', CotationModifiedView)
router.register(r'market_cotations', MarketCotationView)
router.register(r'markets', MarketView)
router.register(r'sports', SportView)
router.register(r'games_today', TodayGamesAdmin)
router.register(r'league_modifieds', LeagueModifiedView)
router.register(r'location_modifieds', LocationModifiedView)


urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('today_games/', TodayGamesView.as_view({'get': 'list'}), name='today_games'),
    path('tomorrow_games/', TomorrowGamesView.as_view({'get': 'list'}), name='tomorrow_games'),
    path('after_tomorrow_games/', AfterTomorrowGamesView.as_view({'get': 'list'}), name='after_tomorrow_games'),
    path('search_games/', SearchGamesView.as_view({'get': 'list'}), name='search_games'),
    path('games_table/', GamesTable.as_view({'get': 'list'}), name='games_table'),
    path('main_menu/', MainMenu.as_view({'get': 'list'})),
    path('games_tomorrow/', GamesTomorrowAdmin.as_view({'get': 'list'}), name='games_tomorrow'),
    path('games_after_tomorrow/', GamesAfterTomorrowAdmin.as_view({'get': 'list'}), name='games_after_tomorrow'),
]

urlpatterns += router.urls

