from django.shortcuts import render,reverse,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward,Country
from user.models import Punter,Seller
from django.core import serializers
from django.conf import settings
from user.models import CustomUser, RandomUser
import json
import urllib
import utils.timezone as tzlocal

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

}


class Home(TemplateResponseMixin, View):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):
		championships = list()
		country = Country.objects.order_by('-priority')
		dict_championship_games = {}
	
		for i in Championship.objects.order_by('-country__priority', '-priority'):			
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.my_games.today_able_games().count() > 0:
					game_set = Game.objects.today_able_games().filter(championship=i)
					dict_championship_games[i] = game_set
					

		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'dict_championship_games': dict_championship_games ,'championships': championships, 'is_seller':is_seller,'countries':country, 'countries_dict':COUNTRY_TRANSLATE}
		

		return self.render_to_response(context)

class TomorrowGames(Home):

	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):
		championships = list()
		country = Country.objects.order_by('-priority')
		dict_championship_games = {}
		

		for i in Championship.objects.order_by('-country__priority','-priority'):
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.my_games.tomorrow_able_games().count() > 0:
					dict_championship_games[i] = Game.objects.tomorrow_able_games().filter(championship=i)				
									

		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'dict_championship_games': dict_championship_games ,'championships': championships, 'is_seller':is_seller,'countries':country, 'countries_dict':COUNTRY_TRANSLATE}
		

		return self.render_to_response(context)


class GameChampionship(TemplateResponseMixin, View):

	template_name = 'core/championship_games.html'

	def get(self, request, *args, **kwargs):
		
		championships = list()
		country = Country.objects.order_by('-priority')
		

		for i in Championship.objects.order_by('-country__priority','-priority'):
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				
				
		championship = Championship.objects.get( pk=int(self.kwargs["pk"]) )
		championship_country = championship.name +" - "+ COUNTRY_TRANSLATE.get(championship.country.name, championship.country.name)
		games = Game.objects.able_games().filter(championship=championship)
	
		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'games': games ,'championships': championships, 'is_seller':is_seller,'countries':country,'countries_dict':COUNTRY_TRANSLATE,'championship_country':championship_country }
		
		return self.render_to_response(context)


class CotationsView(View):
	
	def get(self, request, *args, **kwargs):
		gameid = self.kwargs['gameid']
		
		cotations_by_kind = {}

		cotations_of_game = Cotation.objects.filter(game_id=gameid, is_standard=False)
	
		for cotation in cotations_of_game:
			if cotation.kind not in cotations_by_kind:
				cotations_by_kind[cotation.kind] = []
				cotations_by_kind[cotation.kind].append(cotation)
			else:
				cotations_by_kind[cotation.kind].append(cotation)
		
		cotations_serialized = {}
		for cotation_market in cotations_by_kind:
			cotations_serialized[cotation_market] = serializers.serialize("json", cotations_by_kind[cotation_market] )

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


	def post(self, request, *args, **kwargs):
		

		if request.user.is_authenticated:
			if 'ticket' not in request.session:
				return JsonResponse({'status':403})

			if request.POST.get('ticket_value') == '':
				return JsonResponse({'status':400})
			
			ticket_bet_value = round(float( request.POST.get('ticket_value') ), 2)

			client_name = request.POST.get('nome')
			cellphone = request.POST.get('telefone')

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
					

			if ticket_bet_value < min_bet_value:
				return JsonResponse({'status':410, 'min_bet_value': min_bet_value})

			if ticket_bet_value <= 0:
				return JsonResponse({'status':400})
	
			ticket = BetTicket(
				user=CustomUser.objects.get(pk=request.user.pk),
				value=ticket_bet_value,
				creation_date = tzlocal.now(),
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None),				
				)
				
			cotation_sum = 1
			game_cotations = []
			for game_id in request.session['ticket']:
				game_contation = None
				try:
					game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
					if game_contation.game.start_game_date < tzlocal.now():
						return JsonResponse({'status':409})
					game_cotations.append(game_contation)
					cotation_sum *= game_contation.value
				except Cotation.DoesNotExist:
					return JsonResponse({'status':400})

			ticket_reward_value = round(cotation_sum * ticket_bet_value ,2)
			if float(ticket_reward_value) > float(max_reward_to_pay):
				return JsonResponse({'status':406, 'max_reward_to_pay': max_reward_to_pay}) # NOT ACEPTED

			elif len(game_cotations) < min_number_of_choices_per_bet:
				return JsonResponse({'status':417, 'min_number_of_choices_per_bet': min_number_of_choices_per_bet}) # EXPECTATION FAILED
			else:
				ticket.save()
				if not client_name and not cellphone:
					random_user = None
					ticket.random_user=random_user
					ticket.save()
				else:
					if len(client_name) > 40 or len(cellphone) > 14:
						return JsonResponse({'status':400})
					else:						
						random_user = RandomUser.objects.create(first_name=client_name, cellphone=cellphone)
						ticket.random_user=random_user
						ticket.save()
						ticket.ticket_valid(request.user)
				for game in game_cotations:
					ticket.cotations.add( game )
				ticket.reward.value = ticket_reward_value
				ticket.reward.save()
				return JsonResponse({'ticket_pk': ticket.pk ,'status':201})

		else:
			return JsonResponse({'status':401})
			


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

		for c in ticket.cotations.all():
			content += "<LEFT>" + c.game.name + "<BR>"
			game_date = c.game.start_game_date.strftime('%d/%m/%Y %H:%M')
			content += "<LEFT>" + game_date + "<BR>"
			content += "<LEFT>"+ c.kind + "<BR>"
			content += "<LEFT>" + c.name + " --> " + str(round(c.value, 2)) + "<BR>"

			if c.winning == None:
				content += "<RIGHT> Status: Em Aberto <BR>"
			else:
				content += "<RIGHT> Status: " + ("Acertou" if c.winning else "Não acertou") + "<BR>"
			
			content += "<CENTER>-------------------------------> <BR>"
		content += "<CENTER> "+ settings.APP_VERBOSE_NAME
		content = urllib.parse.urlparse(content).geturl()
		context = {'ticket': ticket, 'print': content, 'valor_apostado': "%.2f" % ticket.value, 'ganho_possivel': "%.2f" % ticket.reward.value}

		return self.render_to_response(context)	


class ResetSellerRevenue(View):

	def get(self, request, *args, **kwargs):

		if not request.user.is_superuser:
			return JsonResponse({'status': 400},json_dumps_params={'ensure_ascii': False})

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
			return redirect(to='/')
		context = {}
		return self.render_to_response(context)


class AppDownload(View, TemplateResponseMixin):

	template_name = 'core/app_download.html'

	def get(self, request):
		return self.render_to_response({})
