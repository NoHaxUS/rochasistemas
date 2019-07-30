from django.urls import path, include
from rest_framework.routers import DefaultRouter
from utils.views.configuration import GeneralConfigurationsView
from utils.views.exclude import  ExcludedGameView, ExcludedLeagueView
from utils.views.rule import RulesMessageView
from utils.views.reward_related import RewardRestricionView
from utils.views.market import MarketModifiedView, MarketRemotionView
from utils.views.comission import SellerComissionView, ManagerComissionView
from utils.views.entry import EntryView
from utils.views.ticket_custom_message import TicketCustomMessageView
from rest_framework_jwt.views import obtain_jwt_token

app_name = 'utils'

router = DefaultRouter()
router.register(r'configurations', GeneralConfigurationsView)
router.register(r'seller_comissions', SellerComissionView)
router.register(r'manager_comissions', ManagerComissionView)
router.register(r'rules', RulesMessageView)
router.register(r'excluded_games', ExcludedGameView)
router.register(r'excluded_leagues', ExcludedLeagueView)
router.register(r'reward_restriction', RewardRestricionView)
router.register(r'markets_reduction', MarketModifiedView)
router.register(r'markets_remotion', MarketRemotionView)
router.register(r'ticket_custom_messages', TicketCustomMessageView)
router.register(r'entries', EntryView)

urlpatterns = [		        
	path('token/', obtain_jwt_token, name='obtain_token'),    
]

urlpatterns += router.urls
