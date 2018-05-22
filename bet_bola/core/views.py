from django.shortcuts import redirect
from django.views import View
from django.core.paginator import Paginator
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward,Country,CotationHistory
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
	"Côte d'Ivoire":"Costa do Marfim",
	"Ukraine":"Ucrânia",
	"Iraq":"Iraque",
	"Cyprus":"Chipre",
	"Georgia":"Geórgia",
	"South Africa":"África do Sul",
	"Romania":"Romênia",
	"Uruguay":"Uruguai",
	"Republic of Ireland":"Irlanda",
	"Bulgaria":"Bulgária"
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

	def get_verbose_cotation(self, cotation_name):
		names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
		return names_mapping.get(cotation_name, cotation_name)
	
	def get(self, request, *args, **kwargs):

		gameid = self.kwargs['gameid']
		cotations_by_kind = {}
		cotations_of_game = Cotation.objects.filter(game_id=gameid, is_standard=False)
	
		for cotation in cotations_of_game:
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
		
		if not request.user.is_authenticated and not client_name:
			data['success'] =  False
			data['action'] = 'random-user'
			data['message'] = 'O nome do cliente é obrigatório.'
		
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

		if data['success'] and float(ticket_reward_value) > float(max_reward_to_pay):
			data['success'] =  False
			data['message'] =  "Desculpe. <br /> Valor máximo da recompensa: R$" + str(round(max_reward_to_pay, 2))

		if data['success'] and len(game_cotations) < min_number_of_choices_per_bet:
			data['success'] =  False
			data['message'] =  "Desculpe. Aposte em pelo menos " + str(min_number_of_choices_per_bet) + " jogo."

		if data['success']:
			ticket = BetTicket(				
				value=ticket_bet_value,
				cotation_value_total=cotation_sum,
				creation_date = tzlocal.now(),
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None)
			)

			if not request.user.has_perm('user.be_seller'):
				if request.user.is_authenticated:
					ticket.user=CustomUser.objects.get(pk=request.user.pk)
				else:
					ticket.random_user=RandomUser.objects.create(first_name=client_name, cellphone=cellphone)				
				ticket.save()
			else:
				user =  CustomUser.objects.get(pk=request.user.pk)
				ticket.user=CustomUser.objects.get(pk=request.user.pk)
				ticket.random_user=RandomUser.objects.create(first_name=client_name, cellphone=cellphone)
				ticket.save()
				if not ticket.validate_ticket(request.user):
					data['success'] =  False
					data['message'] =  "Desculpe. Vendedor não possui limite de credito para efetuar a aposta."
					return UnicodeJsonResponse(data)
			

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
			if ticket.random_user:
				content += "<CENTER> CLIENTE: " + ticket.random_user.first_name + "<BR>"
			else:
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
			content = urllib.parse.urlparse(content).geturl()
			context = {'ticket': ticket, 'print': content,'cotations_values':cotations_values, 'show_ticket': True}
		
		else:
			context = {'show_ticket': False}

		return self.render_to_response(context)	


class ResetSellerRevenue(View):

	def get(self, request, *args, **kwargs):

		if request.user.is_superuser or request.user.has_perm('user.be_manager'):			

			seller_id = int(request.GET['seller_id'])
			tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=seller_id, payment__seller_was_rewarded=False)
			revenue_total = 0

			for ticket in tickets_revenue:
				revenue_total += ticket.value
		
			try:
				seller = Seller.objects.get(pk=seller_id)
				if request.user.has_perm('user.be_manager') and not request.user.has_perm('set_credit_limit', seller):
					return JsonResponse({'status': 405},json_dumps_params={'ensure_ascii': False})		

				dict_response = {'nome': seller.full_name(), 'cpf': seller.cpf, 
					'telefone': seller.cellphone,'faturamento': "%.2f" % revenue_total, 'status': 200}
				
				return JsonResponse(dict_response,json_dumps_params={'ensure_ascii': False})

			except Seller.DoesNotExist:
				return JsonResponse({'status': 404},json_dumps_params={'ensure_ascii': False})		
		else:
			return JsonResponse({'status': 400},json_dumps_params={'ensure_ascii': False})


	def post(self, request, *args, **kwargs):
				
		message = ""
		if request.user.is_superuser or request.user.has_perm('user.be_manager'):
			for quant in range(int(request.POST['quantidade'])):
				
				username = request.POST['vendedor'+str(quant+1)]
				if not Seller.objects.filter(username=username).exists():
				    message += 'Usuário '+ username + ' não existe. </br>'
				else:					
					seller = Seller.objects.get(username=username)

					if request.user.has_perm('set_credit_limit', seller):
						tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=seller.pk, payment__seller_was_rewarded=False)	            	
						payments = Payment.objects.filter(who_set_payment_id=seller.pk, seller_was_rewarded=False)

						for payment in payments:
							payment.seller_was_rewarded = True
							payment.save()
						message += 'Usuário '+ username + ' teve seu faturamento zerado. </br></br>'
					else:
						message += 'Você não tem permissão para zerar o faturamento do usuário '+ username + '. </br>'
	            	           
		else:
			return UnicodeJsonResponse({'message':'Usuário '+ username + ' não tem permissão para zerar faturamento.'})		

		return UnicodeJsonResponse({'message':message})


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
