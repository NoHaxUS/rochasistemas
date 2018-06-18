from django.shortcuts import redirect
from django.views import View
from django.core.paginator import Paginator
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward,Country,CotationHistory
from user.models import Seller
from django.core import serializers
from django.conf import settings
from user.models import CustomUser, NormalUser
import utils.timezone as tzlocal
from utils.utils import no_repetition_list
from utils.response import UnicodeJsonResponse
from django.urls import reverse_lazy
import json
import urllib
from decimal import Decimal


COUNTRY_TRANSLATE = {
	"Brazil":"Brasil",
	"England":"Inglaterra",
	"Spain":"Espanha",
	"France":"França",
	"Germany":"Alemanha",
	"Europe":"Europa",
	"South America": "América do Sul",
	"International":"Internacional",
	"Italy":"Itália",
	"Portugal":"Portugal",
	"Belgium":"Bélgica",
	"USA":"Estados Unidos",
	"Turkey":"Turquia",
	"Netherlands":"Holanda",
	"Russia":"Rússia",
	"Austria":"Áustria",
	"Poland":"Polônia",
	"Angola":"Ângola",
	"Albania":"Albânia",
	"Croatia":"Croácia",
	"Sweden":"Suécia",
	"Malta":"Malta",
	"Saudi Arabia":"Arábia Saudita",
	"Israel":"Israel",
	"Denmark":"Dinamarca",
	"Hong Kong":"Hong Kong",
	"United Arab Emirates":"Emirados Árabes",
	"Finland":"Finlândia",
	"Norway":"Noruega",
	"Greece":"Grécia",
	"Switzerland": "Suíça",
	"Mexico":"México",
	"Ecuador":"Equador",
	"Scotland":"Escócia",
	"Iceland":"Islândia",
	"Saudi Arabia": "Arábia Saudita",
	"India":"Índia",
	"Côte d'Ivoire":"Costa do Marfim",
	"Ukraine":"Ucrânia",
	"Iraq":"Iraque",
	"Cyprus":"Chipre",
	"Georgia":"Geórgia",
	"South Africa":"África do Sul",
	"Romania":"Romênia",
	"Uruguay":"Uruguai",
	"Republic of Ireland":"Irlanda",
	"Bulgaria":"Bulgária",
	"Belarus":"Bielorrússia",
	"Serbia":"Sérvia",
	"Japan":"Japão",
	"Wales":"País de Gales",
	"Cameroon":"Camarões",
	"Egypt":"Egito",
	"Paraguay":"Paraguai",
	"Lithuania":"Lituânia",
	"Estonia":"Estónia",
	"Panama":"Panamá",
	"Indonesia":"Indonésia",
	"Asia":"Ásia",
	"World": "Copa do Mundo",
}


class AllGames(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):

		championships = []
		countries = []
		championship_games = {}
	
		for championship in Championship.objects.all().order_by('-country__priority', '-priority'):
			my_games = championship.my_games.able_games()
			if my_games.count() > 0:
				championships.append(championship)
				countries.append(championship.country)
				my_games_today = my_games.able_games()

				if my_games_today.count() > 0:
					games = my_games_today.filter(championship=championship)
					championship_games[championship] = games


		page = int(request.GET.get('page', 1))
		count = 0
		per_page = 40
		start_count = ((page - 1) * per_page) + 1

		max_count = page * per_page
		
		page_games = {}

		for championship in championship_games:
			count += len(championship_games[championship])
			if count >= start_count:
				page_games[championship] = championship_games[championship]
			else:
				continue
			if count >= max_count:
				break

		total_games = 0
		for championship in championship_games:
			total_games += len(championship_games[championship])

		links = (total_games // per_page) + 1

		print(list(range(links)))
					
		countries = no_repetition_list(countries)
		
		context = {'dict_championship_games': page_games,
		'championships': championships,
		'other_thing': list(range(1,links+1)),
		'actual_page': page,
		'countries':countries, 'countries_dict':COUNTRY_TRANSLATE}
		
		return self.render_to_response(context)


class TodayGames(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):

		championships = []
		countries = []
		championship_games = {}
	
		for championship in Championship.objects.all().order_by('-country__priority', '-priority'):
			my_games = championship.my_games.able_games()
			if my_games.count() > 0:
				championships.append(championship)
				countries.append(championship.country)
				my_games_today = my_games.today_able_games()

				if my_games_today.count() > 0:
					games = my_games_today.filter(championship=championship)
					championship_games[championship] = games
					
		countries = no_repetition_list(countries)
		context = {'dict_championship_games': championship_games ,'championships': championships,
		'countries':countries, 'countries_dict':COUNTRY_TRANSLATE}
		
		return self.render_to_response(context)

class TomorrowGames(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):

		championships = []
		countries = []
		championship_games = {}
		
		for championship in Championship.objects.all().order_by('-country__priority','-priority'):
			if championship.my_games.able_games().count() > 0:
				championships.append(championship)
				countries.append(championship.country)
				if championship.my_games.tomorrow_able_games().count() > 0:
					championship_games[championship] = Game.objects.tomorrow_able_games().filter(championship=championship)		
		
		countries = no_repetition_list(countries)
		context = {'dict_championship_games': championship_games ,'championships': championships,
		'countries':countries, 'countries_dict':COUNTRY_TRANSLATE}

		return self.render_to_response(context)


class GameChampionship(TemplateResponseMixin, View):

	template_name = 'core/championship_games.html'

	def get(self, request, *args, **kwargs):
		
		championships = []
		countries = []
		

		for championship in Championship.objects.order_by('-country__priority','-priority'):
			if championship.my_games.able_games().count() > 0:
				championships.append(championship)
				countries.append(championship.country)
				
				
		championship = Championship.objects.get( pk=self.kwargs["pk"] )
		championship_country = championship.name +" - "+ COUNTRY_TRANSLATE.get(championship.country.name, championship.country.name)
		games = Game.objects.able_games().filter(championship=championship)

		countries = no_repetition_list(countries)

		context = {'games': games ,'championships': championships,
		'countries':countries, 'countries_dict':COUNTRY_TRANSLATE,'championship_country':championship_country }
		
		return self.render_to_response(context)


class CotationsView(View):

	def get_verbose_cotation(self, cotation_name):
		names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
		return names_mapping.get(cotation_name, cotation_name)
	
	def get(self, request, *args, **kwargs):

		gameid = self.kwargs['gameid']
		cotations_by_kind = {}
		cotations_of_game = Cotation.objects.filter(game_id=gameid, is_standard=False)
	
		for cotation in cotations_of_game:
			if cotation.kind:
				if cotation.kind.pk != 976241:
					cotation.name = self.get_verbose_cotation(cotation.name)
				if cotation.kind.name not in cotations_by_kind:
					cotations_by_kind[cotation.kind.name] = []
					cotations_by_kind[cotation.kind.name].append(cotation)
				else:
					cotations_by_kind[cotation.kind.name].append(cotation)
			
		cotations_serialized = {}
		for cotation_market in cotations_by_kind:
			cotations_serialized[cotation_market] = serializers.serialize("json", cotations_by_kind[cotation_market], use_natural_foreign_keys=True)

		data = json.dumps(cotations_serialized)
		return HttpResponse( data, content_type='application/json' )


class BetView(View):

	def post(self, request, *args, **kwargs):		
		if int(request.POST['cotation_id']) < 0:			
			request.session['ticket'] = {}		
			request.session.modified = True
			return JsonResponse({}, status=204)

		if 'ticket' not in request.session:						
			request.session['ticket'] = {}
			request.session['ticket'][request.POST['game_id']] = request.POST['cotation_id']
			request.session.modified = True

			response = HttpResponse()
			response.status_code = 201
			return response
		else:
			request.session['ticket'][request.POST['game_id']] = request.POST['cotation_id']
			request.session.modified = True
			
			response = HttpResponse()
			response.status_code = 201
			return response		

	def get(self, request, *args, **kwargs):
		if 'ticket' not in request.session:
			return HttpResponse("Empty")
		else:
			return JsonResponse( {'ticket': request.session['ticket']})
	
	def delete(self, request, *args, **kwargs):
		pk = self.kwargs["pk"]
		request.session['ticket'].pop(pk)
		request.session.modified = True
		return JsonResponse({}, status=204)


class CreateTicketView(View):

	login_url = reverse_lazy('core:core_home')

	def post(self, request, *args, **kwargs):
		
		from utils.models import GeneralConfigurations

		try:
			general_config = GeneralConfigurations.objects.get(pk=1)
			max_reward_to_pay = general_config.max_reward_to_pay
			min_number_of_choices_per_bet = general_config.min_number_of_choices_per_bet
			min_bet_value = general_config.min_bet_value

		except GeneralConfigurations.DoesNotExist:
			max_reward_to_pay = 50000
			min_number_of_choices_per_bet = 1
			min_bet_value = 1

		data = {
			'success': True
		}

		ticket_value = request.POST.get('ticket_value', None)
		client_name = request.POST.get('nome', None)
		cellphone = request.POST.get('telefone', None)
		
		if not request.user.is_authenticated and not client_name:
			data['success'] =  False
			data['action'] = 'Anon-user'
			data['message'] = 'O nome do cliente é obrigatório.'
			return UnicodeJsonResponse(data)
		
		if request.user.is_superuser or request.user.has_perm('user.be_manager'):
			data['success'] =  False
			data['message'] =  """Desculpe, Contas administradoras ou Gerentes
			não são apropriados para criarem apostas. <br /> 
			Use contas normais ou conta de vendedor."""
			return UnicodeJsonResponse(data)

		if client_name and cellphone:
			if len(client_name) > 40 or len(cellphone) > 14:
				data['success'] =  False
				data['message'] =  "Erro. O nome do cliente precisa ser menor que 40 dígitos e o telefone menor que 14"
				return UnicodeJsonResponse(data)

		if ticket_value == None:
			data['success'] =  False
			data['message'] =  "Valor da aposta inválido."
			return UnicodeJsonResponse(data)

		
		ticket_bet_value = Decimal(ticket_value)
		
		if ticket_bet_value < min_bet_value:
			data['success'] =  False
			data['message'] =  "A aposta mínima é: R$ " + str(min_bet_value)
			return UnicodeJsonResponse(data)

		if 'ticket' not in request.session:
			data['success'] =  False
			data['message'] =  "Selecionar Cotas antes de apostas."
			return UnicodeJsonResponse(data)

		if ticket_bet_value <= 0:
			data['success'] =  False
			data['message'] =  "Valor da aposta inválido."
			return UnicodeJsonResponse(data)

	
		cotation_sum = 1
		game_cotations = []
		for game_id in request.session['ticket']:
			game_contation = None
			try:
				game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
				if game_contation.game.start_game_date < tzlocal.now():
					data['success'] =  False
					data['message'] =  "Desculpe, o jogo:" + game_contation.game.name + " já começou, remova-o"
					return UnicodeJsonResponse(data)

				game_cotations.append(game_contation)
				cotation_sum *= game_contation.value
			except Cotation.DoesNotExist:
				data['success'] =  False
				data['message'] =  "Erro, uma das cotas enviadas não existe."
				return UnicodeJsonResponse(data)


		ticket_reward_value = cotation_sum * ticket_bet_value

		if Decimal(ticket_reward_value) > Decimal(max_reward_to_pay):
			data['success'] =  False
			data['message'] =  "Desculpe. <br /> Valor máximo da recompensa: R$" + str(max_reward_to_pay)
			return UnicodeJsonResponse(data)

		if len(game_cotations) < min_number_of_choices_per_bet:
			data['success'] =  False
			data['message'] =  "Desculpe. Aposte em pelo menos " + str(min_number_of_choices_per_bet) + " jogo."
			return UnicodeJsonResponse(data)

		if data['success']:
			ticket = BetTicket(				
				value=ticket_bet_value,
				cotation_value_total=cotation_sum,
				creation_date = tzlocal.now(),
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None)
			)

			ticket.save()
			if request.user.has_perm('user.be_seller'):
				ticket.seller=CustomUser.objects.get(pk=request.user.pk)
				ticket.normal_user=NormalUser.objects.create(first_name=client_name, cellphone=cellphone)

			else:
				if request.user.is_authenticated:
					ticket.user=CustomUser.objects.get(pk=request.user.pk)
				else:
					ticket.normal_user=NormalUser.objects.create(first_name=client_name, cellphone=cellphone)
			
			ticket.reward.value = ticket_reward_value
			ticket.reward.save()
			ticket.save()

			for i_cotation in game_cotations:
				ticket.cotations.add(i_cotation)
				CotationHistory(
					original_cotation=i_cotation.pk,
					bet_ticket=ticket,
					name=i_cotation.name,
					original_value=i_cotation.original_value,
					value=i_cotation.value,
					game=i_cotation.game,
					winning=i_cotation.winning,
					is_standard=i_cotation.is_standard,
					kind=i_cotation.kind,
					total=i_cotation.total
				).save()
		

			data['message'] = """
				Ticket N° <span class='ticket-number-after-create'> """ +  str(ticket.pk) + """</span>
                <br /> Para acessar detalhes do Ticket, entre no painel do cliente
            	<br /> Realize o pagamento com um de nossos colaboradoes usando o número do Ticket
                <br /><br />
				<a href='/ticket/""" + str(ticket.pk) + """' class='waves-effect waves-light btn text-white see-ticket-after-create hoverable'> Ver Ticket </a>
			"""
			if request.user.has_perm('user.be_seller'):
				if not ticket.validate_ticket(request.user)['success']:
					data['not_validated'] =  "Você não tem saldo para validar o Ticket ! <br />"
					data['message'] = data['not_validated'] + data['message']
					return UnicodeJsonResponse(data)
				else:
					return UnicodeJsonResponse(data)
			else:
				return UnicodeJsonResponse(data)




class TicketDetail(TemplateResponseMixin, View):


	template_name = 'core/ticket_details.html'

	def get_verbose_cotation(self, cotation_name):
		names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
		return names_mapping.get(cotation_name, cotation_name)

	def get(self, request, *args, **kwargs):
		try:
			ticket = BetTicket.objects.get(pk=self.kwargs["pk"])
		except BetTicket.DoesNotExist:
			self.template_name = 'core/ticket_not_found.html'
			return self.render_to_response(context={})

		cotations_history = CotationHistory.objects.filter(bet_ticket=ticket.pk)
		
		if cotations_history.count() > 0:

			cotations_values = {}
			for i_cotation in cotations_history:
				cotations_values[i_cotation.original_cotation] = i_cotation.value


			content = "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
			
			if ticket.seller:
				content += "<CENTER> VENDEDOR: " + ticket.seller.first_name + "<BR>"
			if ticket.normal_user:
				content += "<CENTER> CLIENTE: " + ticket.normal_user.first_name + "<BR>"
			if ticket.user:
				content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

			content += "<CENTER> APOSTA: R$" + str("%.2f" % ticket.value) + "<BR>"
			content += "<CENTER> COTA TOTAL: " + str("%.2f" % ticket.cotation_value_total) + "<BR>"
			content += "<CENTER> GANHO POSSIVEL: R$" + str("%.2f" % ticket.reward.value) + "<BR>"
			
			content += "<CENTER> DATA: " + ticket.creation_date.strftime('%d/%m/%Y %H:%M')
			content += "<BR><BR>"
			
			content += "<LEFT> APOSTAS <BR>"
			content += "<LEFT>-------------------------------> <BR>"

			for cotation in ticket.cotations.all():
				content += "<LEFT>" + cotation.game.name + "<BR>"
				game_date = cotation.game.start_game_date.strftime('%d/%m/%Y %H:%M')
				content += "<LEFT>" + game_date + "<BR>"
				content += "<LEFT>"+ cotation.kind.name + "<BR>"
				content += "<LEFT>" + self.get_verbose_cotation(cotation.name) + " --> " + str("%.2f" % cotations_values[cotation.pk]) + "<BR>"

				if cotation.winning == None:
					content += "<RIGHT> Status: Em Aberto <BR>"
				else:
					content += "<RIGHT> Status: " + ("Acertou" if cotation.winning else "Não acertou") + "<BR>"
				
				content += "<CENTER>-------------------------------> <BR>"
			content += "<CENTER> "+ settings.APP_VERBOSE_NAME + "<BR>"
			content += "<CENTER> Prazo para Resgate do Prêmio: 48 horas."
			content += "#Intent;scheme=quickprinter;package=pe.diegoveloper.printerserverapp;end;"
			
			context = {'ticket': ticket, 'print': content,'cotations_values':cotations_values, 'show_ticket': True}
		else:
			context = {'show_ticket': False}

		return self.render_to_response(context)


class AppDownload(View, TemplateResponseMixin):

	template_name = 'core/app_download.html'

	def get(self, request):
		return self.render_to_response({})
