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
from rest_framework.routers import DefaultRouter
from .views import GeneralConfigurationsView, ExcludedGameView, ExcludedLeagueView, RulesMessageView, RewardRelatedView, MarketReductionView, MarketRemotionView, ComissionView, OverviewView

app_name = 'utils'

router = DefaultRouter()
router.register(r'configurations', GeneralConfigurationsView)
router.register(r'comissions', ComissionView)
router.register(r'rules_message', RulesMessageView)
router.register(r'excluded_games', ExcludedGameView)
router.register(r'excluded_leagues', ExcludedLeagueView)
router.register(r'rewards_related', RewardRelatedView)
router.register(r'markets_reduction', MarketReductionView)
router.register(r'markets_remotion', MarketRemotionView)
router.register(r'overviews', OverviewView)

urlpatterns = router.urls
