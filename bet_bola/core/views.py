from django.shortcuts import redirect
from django.views import View
from django.core.paginator import Paginator
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward,Country
from user.models import Seller
from django.core import serializers
from django.conf import settings
from user.models import CustomUser, RandomUser
import utils.timezone as tzlocal
from utils.utils import no_repetition_list
from utils.response import UnicodeJsonResponse
from django.urls import reverse_lazy
import json
import urllib


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
	"Russia":"Russia",
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

}


class Home(TemplateResponseMixin, View):

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

class TomorrowGames(Home):

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
	
	def get(self, request, *args, **kwargs):

		gameid = self.kwargs['gameid']
		cotations_by_kind = {}
		cotations_of_game = Cotation.objects.filter(game_id=gameid, is_standard=False)
	
		for cotation in cotations_of_game:
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
		
		from user.models import GeneralConfigurations
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
		
		if not request.user.is_authenticated:
			data['success'] =  False
			data['action'] = 'log_in'
		
		if request.user.is_superuser:
			data['success'] =  False
			data['message'] =  """Desculpe. Contas administradoras
			não são apropriadas para criarem apostas. <br /> Use contas normais ou conta de vendedor."""

		if client_name and cellphone:
			if len(client_name) > 40 or len(cellphone) > 14:
				data['success'] =  False
				data['message'] =  "Erro. O nome do cliente precisa ser menor que 40 digitos e o telefone menor que 14"

		if ticket_value == None:
			data['success'] =  False
			data['message'] =  "Valor da aposta inválido."
		else:
			ticket_bet_value = round( float(ticket_value ), 2)
		
			if ticket_bet_value < min_bet_value:
				data['success'] =  False
				data['message'] =  "A aposta mínima é: R$ " + str(round(min_bet_value, 2))

		if 'ticket' not in request.session:
			data['success'] =  False
			data['message'] =  "Selecionar Cotas antes de apostas."

		if ticket_bet_value <= 0:
			data['success'] =  False
			data['message'] =  "Valor da aposta inválido."

	
		cotation_sum = 1
		game_cotations = []
		for game_id in request.session['ticket']:
			game_contation = None
			try:
				game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
				if game_contation.game.start_game_date < tzlocal.now():
					data['success'] =  False
					data['message'] =  "Desculpe, o jogo:" + game_contation.game.name + " já começou, remova-o"
					break
				game_cotations.append(game_contation)
				cotation_sum *= game_contation.value
			except Cotation.DoesNotExist:
				data['success'] =  False
				data['message'] =  "Erro, uma das cotas enviadas não existe."
				break


		ticket_reward_value = round(cotation_sum * ticket_bet_value, 2)

		if float(ticket_reward_value) > float(max_reward_to_pay):
			data['success'] =  False
			data['message'] =  "Desculpe. <br /> Valor máximo da recompensa: R$" + str(round(max_reward_to_pay, 2))

		if len(game_cotations) < min_number_of_choices_per_bet:
			data['success'] =  False
			data['message'] =  "Desculpe. Aposte em pelo menos " + str(min_number_of_choices_per_bet) + " jogos."


		if data['success'] == True:
			ticket = BetTicket(
				user=CustomUser.objects.get(pk=request.user.pk),
				value=ticket_bet_value,
				creation_date = tzlocal.now(),
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None)
			)

			if not request.user.has_perm('user.be_seller'):
				ticket.random_user=None
				ticket.save()
			else:
				ticket.random_user=RandomUser.objects.create(first_name=client_name, cellphone=cellphone)
				ticket.save()
				ticket.validate_ticket(request.user)

			for game in game_cotations:
				ticket.cotations.add(game)
			ticket.reward.value = ticket_reward_value
			ticket.reward.save()

			data['message'] = """
				Ticket N° <span class='ticket-number-after-create'>""" +  str(ticket.pk) + """</span>
                <br /> Para acessar detalhes do Ticket, entre no painel do cliente
            	<br /> Realize o pagamento com um de nossos colaboradoes usando o número do Ticket
                <br /><br />
				<a href='/ticket/""" + str(ticket.pk) + """' class='waves-effect waves-light btn text-white see-ticket-after-create hoverable'> Ver Ticket </a>
			"""

		return UnicodeJsonResponse(data)


class TicketDetail(TemplateResponseMixin, View):


	template_name = 'core/ticket_details.html'

	def get(self, request, *args, **kwargs):
		try:
			ticket = BetTicket.objects.get(pk=self.kwargs["pk"])
		except BetTicket.DoesNotExist:
			self.template_name = 'core/ticket_not_found.html'
			return self.render_to_response(context={})

		content = "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
		if ticket.random_user:
			content += "<CENTER> CLIENTE: " + ticket.random_user.first_name + "<BR>"
		else:
			content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"
		content += "<CENTER> APOSTA: R$" + str(ticket.value) + "<BR>"
		content += "<CENTER> GANHO POSSIVEL: R$" + str(ticket.reward.value) + "<BR>"
		
		content += "<CENTER> DATA: " + ticket.creation_date.strftime('%d/%m/%Y %H:%M')
		content += "<BR><BR>"
		
		content += "<LEFT> APOSTAS <BR>"
		content += "<LEFT>-------------------------------> <BR>"

		for cotation in ticket.cotations.all():
			content += "<LEFT>" + cotation.game.name + "<BR>"
			game_date = cotation.game.start_game_date.strftime('%d/%m/%Y %H:%M')
			content += "<LEFT>" + game_date + "<BR>"
			content += "<LEFT>"+ cotation.kind.name + "<BR>"
			content += "<LEFT>" + cotation.name + " --> " + str(round(cotation.value, 2)) + "<BR>"

			if cotation.winning == None:
				content += "<RIGHT> Status: Em Aberto <BR>"
			else:
				content += "<RIGHT> Status: " + ("Acertou" if cotation.winning else "Não acertou") + "<BR>"
			
			content += "<CENTER>-------------------------------> <BR>"
		content += "<CENTER> "+ settings.APP_VERBOSE_NAME + "<BR>"
		content += "<CENTER> Prazo para Resgate do Prêmio: 48 horas."
		content = urllib.parse.urlparse(content).geturl()
		context = {'ticket': ticket, 'print': content, 'valor_apostado': "%.2f" % ticket.value, 'ganho_possivel': "%.2f" % ticket.reward.value}

		return self.render_to_response(context)	


class ResetSellerRevenue(View):

	def get(self, request, *args, **kwargs):

		if request.user.is_superuser:
	
			seller_id = int(request.GET['seller_id'])
			tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=seller_id, payment__seller_was_rewarded=False)
			revenue_total = 0

			for ticket in tickets_revenue:
				revenue_total += ticket.value
		
			try:
				seller = Seller.objects.get(pk=seller_id)
				
				dict_response = {'nome': seller.full_name(), 'cpf': seller.cpf, 
					'telefone': seller.cellphone,'faturamento': "%.2f" % revenue_total, 'status': 200}
				
				return JsonResponse(dict_response,json_dumps_params={'ensure_ascii': False})

			except Seller.DoesNotExist:
				return JsonResponse({'status': 404},json_dumps_params={'ensure_ascii': False})

		else:
			return JsonResponse({'status': 400},json_dumps_params={'ensure_ascii': False})


	def post(self, request, *args, **kwargs):
		
		seller_id = int(request.POST['seller_id'])
		payments = Payment.objects.filter(who_set_payment_id=seller_id, seller_was_rewarded=False)

		for payment in payments:
			payment.seller_was_rewarded = True
			payment.save()

		return JsonResponse({'status': 200},json_dumps_params={'ensure_ascii': False})


class GeneralConf(TemplateResponseMixin, View):
	template_name = 'core/admin_panel.html'

	def get(self, request, *args, **kwargs):
		if not request.user.is_superuser:
			return redirect('core:core_home')
		return self.render_to_response({})


class AppDownload(View, TemplateResponseMixin):

	template_name = 'core/app_download.html'

	def get(self, request):
		return self.render_to_response({})
