from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.db.models import Q
from .serializers import GeneralConfigurationsSerializer, ExcludedGameSerializer, ExcludedLeagueSerializer, RulesMessageSerializer, RewardRelatedSerializer, MarketReductionSerializer, MarketRemotionSerializer, ComissionSerializer, OverviewSerializer
from ticket.serializers import TicketSerializer
from .models import GeneralConfigurations, ExcludedGame, ExcludedLeague, RulesMessage, RewardRelated, MarketReduction, MarketRemotion, Comission, Overview
from ticket.models import Ticket
from user.models import Seller
from .permissions import General, Balance, ManagerAndSellerConflict, Date


class GeneralConfigurationsView(ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer
    permission_classes = [General,]


class RulesMessageView(ModelViewSet):
	queryset = RulesMessage.objects.all()
	serializer_class = RulesMessageSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rules= RulesMessage.objects.filter(store=store)
		serializer = self.get_serializer(rules, many=True)

		return Response(serializer.data)


class ExcludedGameView(ModelViewSet):
	queryset = ExcludedGame.objects.all()
	serializer_class = ExcludedGameSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		excluded_game= ExcludedGame.objects.filter(store=store)
		serializer = self.get_serializer(excluded_game, many=True)

		return Response(serializer.data)


class ExcludedLeagueView(ModelViewSet):
	queryset = ExcludedLeague.objects.all()
	serializer_class = ExcludedLeagueSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		excluded_league= ExcludedLeague.objects.filter(store=store)
		serializer = self.get_serializer(excluded_league, many=True)

		return Response(serializer.data)


class RewardRelatedView(ModelViewSet):
	queryset = RewardRelated.objects.all()
	serializer_class = RewardRelatedSerializer
	permission_classes = [General,]


	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rewards_related= RewardRelated.objects.filter(store=store)
		serializer = self.get_serializer(rewards_related, many=True)

		return Response(serializer.data)


class MarketReductionView(ModelViewSet):
	queryset = MarketReduction.objects.all()
	serializer_class = MarketReductionSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		markets_reduction= MarketReduction.objects.filter(store=store)
		serializer = self.get_serializer(markets_reduction, many=True)

		return Response(serializer.data)


class MarketRemotionView(ModelViewSet):
	queryset = MarketRemotion.objects.all()
	serializer_class = MarketRemotionSerializer

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		markets_remotion= MarketRemotion.objects.filter(store=store)
		serializer = self.get_serializer(markets_remotion, many=True)

		return Response(serializer.data)


class ComissionView(ModelViewSet):
	queryset = Comission.objects.all()
	serializer_class = ComissionSerializer
	permission_classes = [General, ]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)	

		comission = Comission.objects.filter(store=store)

		if request.user.has_perm('user.be_seller') and not request.user.is_superuser:
			comission = comission.filter(seller_related=request.user.seller)
		if request.user.has_perm('user.be_manager') and not request.user.is_superuser:
			comission = comission.filter(seller_related__my_manager=request.user.manager)

		serializer = self.get_serializer(comission, many=True)

		return Response(serializer.data)

class Balance(APIView):
	permission_classes = [Balance,ManagerAndSellerConflict, Date]

	def get(self, request):
		store_id = request.GET.get('store')
		seller = request.GET.get('seller')				
		_from = request.GET.get('from')
		_to = request.GET.get('to')
		manager = request.GET.get('manager')				
		itens = {}
		if seller:
			seller = Seller.objects.get(username=seller)			
			comissions = Comission.objects.get(seller_related=seller).total_comission(None, None)
			tickets = Ticket.objects.filter(seller=seller)
			if _from and _to:			
				comissions = Comission.objects.get(seller_related=seller).total_comission(_from, _to)
				tickets = Ticket.objects.filter(seller=seller).filter(Q(creation_date__date__gte=_from) & Q(creation_date__date__lte=_to))
			tickets_count = tickets.count()
			entries = tickets.aggregate(value_sum=Sum('value'))['value_sum']
			outs = seller.out_money()
			balance = entries - (outs + comissions)
			tickets = TicketSerializer(tickets, many=True)
			itens = {'seller':seller.username, 'comissions':comissions, 'tickets_quantity':tickets_count,'tickets':tickets.data	, 'entries':entries, 'outs': outs, 'balance':balance}
			return Response(itens)

		sellers = Seller.objects.filter(my_store__pk=store_id)
		if manager:
			sellers = sellers.filter(my_manager__username=manager)
		for seller in sellers:			
			seller = Seller.objects.get(username=seller)
			comissions = Comission.objects.get(seller_related=seller).total_comission(None, None)
			tickets = Ticket.objects.filter(seller=seller)
			comissions = Comission.objects.get(seller_related=seller).total_comission(None, None)
			tickets = Ticket.objects.filter(seller=seller)
			if _from and _to:			
				comissions = Comission.objects.get(seller_related=seller).total_comission(_from, _to)
				tickets = Ticket.objects.filter(seller=seller).filter(Q(creation_date__date__gte=_from) & Q(creation_date__date__lte=_to))
			tickets_count = tickets.count()			
			entries = tickets.aggregate(value_sum=Sum('value')).get('value_sum') 
			entries = entries if entries else 0
			outs = seller.out_money()						
			balance = entries - (outs + comissions)
			tickets = TicketSerializer(tickets, many=True)
			itens[seller.username] = {'comissions':comissions, 'tickets_quantity':tickets_count, 'tickets':tickets.data, 'entries':entries, 'outs': outs, 'balance':balance}

		return Response(itens)

class OverviewView(ModelViewSet):
	queryset = Overview.objects.all()
	serializer_class = OverviewSerializer
	permission_classes = [General, ]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)	

		overview = Overview.objects.filter(store=store)
		

		serializer = self.get_serializer(overview, many=True)

		return Response(serializer.data)

	
