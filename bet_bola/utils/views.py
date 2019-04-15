from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from .serializers import GeneralConfigurationsSerializer, ExcludedGameSerializer, ExcludedLeagueSerializer, RulesMessageSerializer, RewardRelatedSerializer, MarketReductionSerializer, MarketRemotionSerializer, ComissionSerializer
from .models import GeneralConfigurations, ExcludedGame, ExcludedLeague, RulesMessage, RewardRelated, MarketReduction, MarketRemotion, Comission
from .permissions import General


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
		store_id = request.GE('store')
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
		store_id = request.GE('store')
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
		store_id = request.GE('store')
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
		store_id = request.GE('store')
		store = Store.objects.get(pk=store_id)

		markets_reduction= MarketReduction.objects.filter(store=store)
		serializer = self.get_serializer(markets_reduction, many=True)

		return Response(serializer.data)


class MarketRemotionView(ModelViewSet):
	queryset = MarketRemotion.objects.all()
	serializer_class = MarketRemotionSerializer

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GE('store')
		store = Store.objects.get(pk=store_id)

		markets_remotion= MarketRemotion.objects.filter(store=store)
		serializer = self.get_serializer(markets_remotion, many=True)

		return Response(serializer.data)

class ComissionView(ModelViewSet):
	queryset = Comission.objects.all()
	serializer_class = ComissionSerializer

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GE('store')
		store = Store.objects.get(pk=store_id)	

		comission = Comission.objects.filter(store=store)

		if request.user.has_perm('user.be_seller'):
			comission = comission.filter(seller_related=request.user.seller)
		if request.user.has_perm('user.be_manager'):
			comission = comission.filter(seller_related__my_manager=request.user.manager)

		serializer = self.get_serializer(comission, many=True)

		return Response(serializer.data)

# class ValidateTicket(View):

#     def post(self, request, *args, **kwargs):
#         ticket_id = request.POST['ticket_id']

#         ticket = Ticket.objects.filter(pk=ticket_id)

#         if ticket.count() > 0:
#             return UnicodeJsonResponse(ticket.first().validate_ticket(request.user.seller))
#         else:
#             return UnicodeJsonResponse({
#                 'sucess':False,
#                 'message': 'Esse bilhete não existe.'
#             })


# class CancelTicket(View):

#     def post(self, request, *args, **kwargs):
#         ticket_id = request.POST['ticket_id']

#         ticket = Ticket.objects.filter(pk=ticket_id)

#         if ticket.count() > 0:
#             return UnicodeJsonResponse(ticket.first().cancel_ticket(request.user.seller))
#         else:
#             return UnicodeJsonResponse({
#                 'sucess':False,
#                 'message': 'Esse bilhete não existe.'
#             })


# class PayTicketWinners(View):

#     def post(self, request, *args, **kwargs):
#         if request.user.is_superuser:
#             tickets = Ticket.objects.annotate(cotations_open=Count('cotations__pk', filter=Q(cotations__status=1)) )\
#             .annotate(cotations_not_winner=Count('cotations__pk', filter=~Q(cotations__settlement__in=[2,5]) & ~Q(cotations__status=2) ) )\
#             .filter(cotations_open=0, cotations_not_winner=0, payment__status_payment='Pago')\
#             .exclude(reward__reward_status=Reward.REWARD_STATUS[1][1])

#             for ticket in tickets:
#                 ticket.pay_winner_punter(ticket.payment.who_set_payment)

#             return UnicodeJsonResponse({
#                 'sucess':True,
#                 'message': 'Ganhadores Pagos.'
#             })
#         return UnicodeJsonResponse({
#             'sucess':False,
#             'message': 'Você não tem permissão para isso.'
#         })


# class GetMainMenuView(View):

#     def get(self, request, *args, **kwargs):

#         games = Game.objects.filter(start_date__gt=tzlocal.now(),
#         league__isnull=False,
#         game_status__in=[1,8,9],
#         visible=True)\
#         .annotate(cotations_count=Count('cotations'))\
#         .filter(cotations_count__gte=3)\
#         .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
#         .order_by('-league__location__priority', '-league__priority')\
#         .values('league__location','league__location__name', 'league')\
#         .distinct()


#         itens = {}
#         for value in games:
#             value["league__name"] = League.objects.filter(id=value['league']).values('name').first()['name']
#             if not value['league__location__name'] in itens.keys():
#                 itens[value['league__location__name']] = []
#                 itens[value['league__location__name']].append( ( value['league'], value["league__name"]) )
#             else:
#                 itens[value['league__location__name']].append( ( value['league'], value["league__name"]) )


#         return UnicodeJsonResponse(itens, safe=False)


# class PDF(View):


#     def get(self, request, *args, **kwargs):
#         ticket = get_object_or_404(Ticket, pk=self.kwargs["pk"])
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'inline; filename="ticket.pdf"'


#         cotations_history = CotationHistory.objects.filter(ticket=ticket.pk)

#         cotations_values = {}
#         for i_cotation in cotations_history:
#             cotations_values[i_cotation.original_cotation.pk] = i_cotation.price


#         pdf = FPDF('P', 'mm', (231, 297 + ticket.cotations.count() * 84))
#         pdf.add_page()
#         pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)		
#         pdf.set_font('DejaVu','',30)

#         pdf.text(60,15, "-> "+ settings.APP_VERBOSE_NAME.upper() +" <-")
#         pdf.text(55,30, 'BILHETE:' + str(ticket.pk))

#         if ticket.seller:
#             pdf.text(55,96, 'CAMBISTA: ' + ticket.seller.first_name)
#         if ticket.normal_user:
#             pdf.text(55,40, 'CLIENTE:' + ticket.normal_user.first_name)
#         if ticket.user:
#             pdf.text(55,40, 'CLIENTE:' + ticket.user.first_name)
								
#         pdf.text(55,50, 'DATA: ' + ticket.creation_date.strftime('%d/%m/%Y %H:%M'))
#         pdf.text(55,60, "APOSTA: R$" + str("%.2f" % ticket.value) )
#         pdf.text(55,72, "COTA TOTAL: " + str("%.2f" % ticket.cotation_sum() ))
#         if ticket.reward:
#             pdf.text(55,84, "GANHO POSSÍVEL: R$" + str("%.2f" % ticket.reward.real_value) )
#         if ticket.payment:
#             payment_text = ticket.payment.status_payment
#             if len(payment_text) <= 5:
#                 pdf.text(55,107, "STATUS: " + payment_text )
#             else:
#                 pdf.text(10,107, "STATUS: " + payment_text )
        
#         pdf.text(4,130,'APOSTAS')		
#         pdf.text(0, 135,'--------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
#         h = 140
        
#         for c in ticket.cotations.all():
#             h=h+8
#             pdf.text(4,h,c.game.name)
#             h=h+14
#             pdf.text(4,h, c.game.start_date.strftime('%d/%m/%Y %H:%M'))
#             if c.market:
#                 h=h+14
#                 pdf.text(4,h, c.market.name)
#             h=h+14
#             base_line = c.base_line if c.base_line else ''
#             pdf.text(4,h,"Cota:" + c.name + ' ' + base_line)			
#             pdf.text(190,h,str("%.2f" % cotations_values[c.pk]))
#             h=h+14

#             pdf.text(4,h,"Status:")			
#             pdf.text(170,h, c.get_settlement_display_modified() )				


#             h=h+14
#             pdf.text(0,h,'---------------------------------------------------------------------------------------------------------------------------------------------------------')			

#         pdf.text(80,h+20, settings.APP_VERBOSE_NAME)
#         h+=36
#         if TicketCustomMessage.objects.first():
            
#             phrases = TicketCustomMessage.objects.first().text.replace("\r","").split("\n")            

#             for phrase in phrases:                                
#                 v = 20
#                 pdf.text(v,h, phrase)
#                 h+=10

#         buffer = pdf.output(dest='S').encode('latin-1')
#         response.write(buffer)
#         return response


# class GamesTablePDF(View):
#     def order_cotations(self, cotations):
#         ordered = list(cotations).copy()
#         for cotation in cotations:
#             if cotation.name == 'Casa':
#                 ordered[0] = cotation
#             elif cotation.name == "Empate":
#                 ordered[1] = cotation
#             elif cotation.name == "Fora":
#                 ordered[2] = cotation
#             elif cotation.name == "Casa/Fora":
#                 ordered[3] = cotation
#             elif cotation.name == "Casa/Empate":
#                 ordered[4] = cotation
#             elif cotation.name == "Empate/Fora":
#                 ordered[5] = cotation
#         return ordered         


#     def get(self, request, *args, **kwargs):        
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = 'inline; filename="ticket.pdf"'

#         my_qs = Cotation.objects.filter(Q(market__name="1X2") | Q(market__pk=7), status=1)

#         games = Game.objects.filter(start_date__gt=tzlocal.now(), 
#         start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
#         game_status=1, 
#         visible=True)\
#         .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
#         .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
#         .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
#         .order_by('-league__location__priority','-league__priority')

#         league_games = defaultdict(list)
#         dictionare = {"Casa":"C", "Empate":"E","Fora":"F","Casa/Fora":"C/F","Casa/Empate":"C/E","Empate/Fora":"E/F"}  

#         for game in games:
#             league_games[game.league].append(game)        

#         pdf = FPDF('P', 'mm', (231, 297 + games.count() * 64))
#         pdf.add_page()
#         pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)     
#         pdf.set_font('DejaVu','',30)

#         #pdf.text(60,15, "-> "+ settings.APP_VERBOSE_NAME.upper() +" <-")                
        
#         h = 10
#         for league in league_games:
#             h=h+8
#             pdf.text(4,h,league.name.upper())
#             pdf.set_font('DejaVu','',28)
#             for game in league_games[league]:
#                 h=h+15
#                 pdf.text(4,h, game.name)                
#                 h=h+14
#                 cont = 0
#                 content = ""
#                 for c in self.order_cotations(game.my_cotations): 
#                     content += "[" + dictionare[c.name] + ':' + str(c.price)  +"]"                                                    
#                     if cont == 2:
#                         pdf.text(5,h,content)
#                         content = ""
#                         h=h+14     
#                     cont +=1                     
#                 pdf.text(5,h,content)                
#                 h=h+15
#             #h=h+1
#             pdf.set_font('DejaVu','',30)
#         pdf.text(80,h+20, settings.APP_VERBOSE_NAME)
#         h+=10
        
#         buffer = pdf.output(dest='S').encode('latin-1')
#         response.write(buffer)
#         return response

