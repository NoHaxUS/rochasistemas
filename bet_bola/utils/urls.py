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
from .my_views.configuration import GeneralConfigurationsView
from .my_views.exclude import  ExcludedGameView, ExcludedLeagueView
from .my_views.rule import RulesMessageView
from .my_views.reward_related import RewardRelatedView
from .my_views.market import MarketReductionView, MarketRemotionView
from .my_views.comission import SellerComissionView, ManagerComissionView
from .my_views.release import ReleaseView
from .my_views.ticket_custom_message import TicketCustomMessageView
#  OverviewView, Balance, 
from rest_framework_jwt.views import obtain_jwt_token

app_name = 'utils'

router = DefaultRouter()
router.register(r'configurations', GeneralConfigurationsView)
router.register(r'seller_comissions', SellerComissionView)
router.register(r'manager_comissions', ManagerComissionView)
router.register(r'rules', RulesMessageView)
router.register(r'excluded_games', ExcludedGameView)
router.register(r'excluded_leagues', ExcludedLeagueView)
router.register(r'rewards_related', RewardRelatedView)
router.register(r'markets_reduction', MarketReductionView)
router.register(r'markets_remotion', MarketRemotionView)
router.register(r'ticket_custom_messages', TicketCustomMessageView)
router.register(r'release', ReleaseView)

urlpatterns = [		        
	path('token/', obtain_jwt_token, name='obtain_token'),    
]

urlpatterns += router.urls
