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
from django.db.models import Prefetch, Count
from django.utils import timezone
from math import ceil
from  collections import defaultdict

def get_main_menu():

	games = Game.objects.filter(start_game_date__gt=tzlocal.now(),
	championship__isnull=False,
	status_game="NS",
	is_visible=True)\
	.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
	.order_by('-championship__country__priority', '-championship__priority')


	country_leagues = defaultdict(set)

	for game in games:
		country_leagues[game.championship.country].add(game.championship)
	return country_leagues

class TodayGames(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):
		
		
		
		page = int(request.GET.get('page')) if request.GET.get('page') else 1

		results_per_page = 80
		start_offset = 0 if page == 1 else (page * results_per_page) - results_per_page
		end_offset = (page * results_per_page)
		
		after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)
		my_qs = Cotation.objects.filter(is_standard=True)
		
		games = Game.objects.filter(start_game_date__gt=tzlocal.now(), 
		start_game_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
		status_game="NS", 
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
		.order_by('-championship__country__priority','-championship__priority')[start_offset:end_offset]


		games_total = Game.objects.filter(start_game_date__gt=tzlocal.now(), 
		start_game_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
		status_game="NS", 
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.count()
		
		num_of_pages =  ceil(games_total / results_per_page)

		league_games = defaultdict(list)
		country_leagues = get_main_menu()
		
		for game in games:
			league_games[game.championship].append(game)
		
		context = {'league_games': league_games, 
			'country_leagues': country_leagues,
			'after_tommorrow': after_tommorrow,
			'range_pages': range(1, num_of_pages + 1),
			'current_page': page}
		
		return self.render_to_response(context)

class TomorrowGames(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):

		page = int(request.GET.get('page')) if request.GET.get('page') else 1

		results_per_page = 80
		start_offset = 0 if page == 1 else (page * results_per_page) - results_per_page
		end_offset = (page * results_per_page)

		after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)

		my_qs = Cotation.objects.filter(is_standard=True)
		games = Game.objects.filter(start_game_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
		status_game="NS", 
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
		.order_by('-championship__country__priority','-championship__priority')[start_offset:end_offset]


		games_total = Game.objects.filter(start_game_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
		status_game="NS", 
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.count()

		num_of_pages =  ceil(games_total / results_per_page)
		
		league_games = defaultdict(list)
		country_leagues = get_main_menu()
		
		for game in games:
			league_games[game.championship].append(game)
		
		context = {'league_games': league_games, 
			'country_leagues': country_leagues,
			'after_tommorrow': after_tommorrow,
			'range_pages': range(1, num_of_pages + 1),
			'current_page': page
			}


		return self.render_to_response(context)



class AfterTomorrowGames(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):

		page = int(request.GET.get('page')) if request.GET.get('page') else 1

		results_per_page = 80
		start_offset = 0 if page == 1 else (page * results_per_page) - results_per_page
		end_offset = (page * results_per_page)

		after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)

		my_qs = Cotation.objects.filter(is_standard=True)
		games = Game.objects.filter(start_game_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
		status_game="NS", 
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
		.order_by('-championship__country__priority','-championship__priority')[start_offset:end_offset]


		games_total = Game.objects.filter(start_game_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
		status_game="NS", 
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.count()

		num_of_pages =  ceil(games_total / results_per_page)

		league_games = defaultdict(list)
		country_leagues = get_main_menu()
		
		for game in games:
			league_games[game.championship].append(game)
		
		context = {'league_games': league_games, 
			'country_leagues': country_leagues,
			'after_tommorrow': after_tommorrow,
			'range_pages': range(1, num_of_pages + 1),
			'current_page': page
			}
		
		return self.render_to_response(context)



class GameChampionship(TemplateResponseMixin, View):

	template_name = 'core/championship_games.html'

	def get(self, request, *args, **kwargs):

		after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)

		my_qs = Cotation.objects.filter(is_standard=True)

		games = Game.objects.filter(start_game_date__gt=tzlocal.now(),
		status_game="NS",
		championship__id=self.kwargs["pk"],
		is_visible=True)\
		.annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
		.prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
		.order_by('-championship__priority')
		
		
		country_leagues = get_main_menu()

		first_game = games.first()
		country_league = str(first_game.championship.country.name) + " - " + str(first_game.championship.name)
		context = {'games_selected_league': games, 
			'country_leagues': country_leagues,
			'country_league' : country_league,
			'after_tommorrow': after_tommorrow}

		return self.render_to_response(context)


class CotationsView(View):

	def get_verbose_cotation(self, cotation_name):
		names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
		return names_mapping.get(cotation_name, cotation_name)
	
	def get(self, request, *args, **kwargs):

		gameid = self.kwargs['gameid']
		cotations_by_kind = {}
		cotations_of_game = Cotation.objects.filter(game_id=gameid, is_standard=False, kind__isnull=False)
	
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


def get_max_reward_by_value(value, actual_max_value):
	from math import ceil
	values_rewards = {}
	return values_rewards.get(ceil(value), actual_max_value)

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
			max_bet_value = general_config.max_bet_value
			min_cotation_sum = general_config.min_cotation_sum
			max_cotation_sum = general_config.max_cotation_sum

		except GeneralConfigurations.DoesNotExist:
			max_bet_value = 1000000
			max_reward_to_pay = 50000
			min_number_of_choices_per_bet = 1
			min_bet_value = 1
			min_cotation_sum = 1
			max_cotation_sum = 100000

		data = {
			'success': True
		}

		ticket_value = request.POST.get('ticket_value', None)
		client_name = request.POST.get('client_name', None)
		cellphone = request.POST.get('telefone', None)

		accepted_conditions = request.POST.get('accepted_conditions', False)
		
		if not request.user.is_authenticated or request.user.has_perm('user.be_seller'):
			if not client_name or len(client_name) < 4:
				data['success'] =  False
				data['message'] =  "Digite o nome do cliente (4 dígitos ou mais)."
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
				data['message'] =  "Erro, O nome do cliente precisa ser menor que 40 dígitos e o telefone menor que 14."
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

		if ticket_bet_value > max_bet_value:
			data['success'] =  False
			data['message'] =  "A aposta máxima é: R$ " + str(max_bet_value)
			return UnicodeJsonResponse(data)

		if 'ticket' not in request.session:
			data['success'] =  False
			data['message'] =  "Selecione algumas cotações."
			data['clear_cookies'] = True
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


		if cotation_sum < min_cotation_sum:
			data['success'] =  False
			data['message'] =  "A cotação total deve ser maior que "+ str(min_cotation_sum)
			return UnicodeJsonResponse(data)

		if cotation_sum > max_cotation_sum:
			data['success'] =  False
			data['message'] =  "A cotação total deve ser menor que "+ str(max_cotation_sum)
			return UnicodeJsonResponse(data)

		ticket_reward_value = cotation_sum * ticket_bet_value

		max_reward_to_pay_per_value = get_max_reward_by_value(ticket_bet_value, max_reward_to_pay)

		if not accepted_conditions:
			if Decimal(ticket_reward_value) > max_reward_to_pay_per_value:
				data['success'] =  False
				data['has_to_accept'] = True
				data['message'] =  "O valor máximo pago pela banca para o valor apostado é: R$" + str(max_reward_to_pay_per_value) + ". Seu prêmio será reajustado para esse valor."
				return UnicodeJsonResponse(data)

		if len(game_cotations) < min_number_of_choices_per_bet:
			data['success'] =  False
			data['message'] =  "Desculpe, Aposte em pelo menos " + str(min_number_of_choices_per_bet) + " jogo."
			return UnicodeJsonResponse(data)

		if data['success']:
			ticket = BetTicket(				
				value=ticket_bet_value,
				creation_date = tzlocal.now(),
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None)
			)
			ticket.save()

			if request.user.has_perm('user.be_seller'):
				ticket.seller=request.user.seller
				ticket.normal_user=NormalUser.objects.create(first_name=client_name, cellphone=cellphone)
			else:
				if request.user.is_authenticated:
					ticket.user=request.user.punter
				else:
					ticket.normal_user=NormalUser.objects.create(first_name=client_name, cellphone=cellphone)
			
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
					data['not_validated'] =  "<span class='no_credit_message'> Você não tem saldo para validar o Ticket !!! <br /></span>"
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
		
		if cotations_history.count() > 0 and ticket.is_visible == True:

			cotations_values = {}
			for i_cotation in cotations_history:
				cotations_values[i_cotation.original_cotation] = i_cotation.value

			content = "<CENTER> -> " + settings.APP_VERBOSE_NAME.upper() + " <- <BR>"
			content += "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
			
			if ticket.seller:
				content += "<CENTER> VENDEDOR: " + ticket.seller.first_name + "<BR>"
			if ticket.normal_user:
				content += "<CENTER> CLIENTE: " + ticket.normal_user.first_name + "<BR>"
			if ticket.user:
				content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

			content += "<CENTER> APOSTA: R$" + str("%.2f" % ticket.value) + "<BR>"
			content += "<CENTER> COTA TOTAL: " + str("%.2f" % ticket.cotation_sum() ) + "<BR>"
			if ticket.reward:
				content += "<CENTER> GANHO POSSIVEL: R$" + str("%.2f" % ticket.reward.real_value) + "<BR>"
			if ticket.payment:
				content +=  "<CENTER> STATUS: " + ticket.payment.status_payment + "<BR>"
			content += "<CENTER> DATA: " + ticket.creation_date.strftime('%d/%m/%Y %H:%M')
			content += "<BR><BR>"
			
			content += "<LEFT> APOSTAS <BR>"
			content += "<LEFT>-------------------------------> <BR>"

			for cotation in ticket.cotations.all():
				content += "<LEFT>" + cotation.game.name + "<BR>"
				game_date = cotation.game.start_game_date.strftime('%d/%m/%Y %H:%M')
				content += "<LEFT>" + game_date + "<BR>"
				if cotation.kind:
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
			
			context = {'ticket': ticket, 
			'print': content,'cotations_values':cotations_values, 
			'show_ticket': True, 'base_url': request.get_host()}
		else:
			context = {'show_ticket': False}

		return self.render_to_response(context)


class AppDownload(View, TemplateResponseMixin):

	template_name = 'core/app_download.html'

	def get(self, request):
		return self.render_to_response({})
