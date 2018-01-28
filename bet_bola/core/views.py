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
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward
from user.models import Punter,Seller
from django.core import serializers
from django.conf import settings
from user.models import CustomUser, RandomUser
import json
import urllib
import utils.timezone as tzlocal

COUNTRY_TRANSLATE = {
	"Austria":"Áustria",
	"England":"Inglaterra",
	"Turkey":"Turquia",
	"Germany":"Alemanha",
	"Poland":"Polônia",
	"France":"França",
	"Angola":"Ângola",
	"Albania":"Albânia",
	"Croatia":"Croácia",
	"Italy":"Itália",
	"Sweden":"Suécia",
	"Spain":"Espanha",
	"Malta":"Malta",
	"Brazil":"Brasil",
	"Saudi Arabia":"Arábia Saudita",
	"Israel":"Israel",
	"Denmark":"Dinamarca",
	"Russia":"Russia",
	"Hong Kong":"Hong Kong",
	"International":"Internacional",
	"Belgium":"Bélgica",
	"USA":"Estados Unidos",
	"Europe":"Europa",
	"Netherlands":"Holanda",
	"Portugal":"Portugal",
	"United Arab Emirates":"Emirados Árabes",
	"Finland":"Finlândia",
	"Norway":"Noruega"

}


class Home(TemplateResponseMixin, View):
	template_name = 'core/index.html'


	def get(self, request, *args, **kwargs):
		championships = list()
		country = list()
		dict_championship_games = {}
		
		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.my_games.today_able_games().count() > 0:

					game_set = Game.objects.today_able_games().filter(championship=i)
					
					dict_championship_games[i] = game_set

				if i.country not in country:					
					country.append(i.country)

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
	dict_championship_games = {}


	def get(self, request, *args, **kwargs):
		championships = list()
		country = list()
		
		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.my_games.tomorrow_able_games().count() > 0:
					self.dict_championship_games[i] = Game.objects.tomorrow_able_games().filter(championship=i)				
				if i.country not in country:					
					country.append(i.country)

		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'dict_championship_games': self.dict_championship_games ,'championships': championships, 'is_seller':is_seller,'countries':country, 'countries_dict':COUNTRY_TRANSLATE}
		

		return self.render_to_response(context)

		

class GeneralConf(TemplateResponseMixin, View):
	template_name = 'core/admin_conf.html'

	def get(self, request, *args, **kwargs):
		if not request.user.is_superuser:
			return redirect(to='/')
		context = {}
		return self.render_to_response(context)




class GameChampionship(TemplateResponseMixin, View):
	template_name = 'core/championship_games.html'	
	form = AuthenticationForm()


	def get(self, request, *args, **kwargs):
		championships = list()
		country = list()
		
		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.country not in country:					
					country.append(i.country)
				

		championship = Championship.objects.get( pk=int(self.kwargs["pk"]) )
		games = Game.objects.able_games().filter(championship=championship)
	
		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'games': games ,'championships': championships,'form': self.form, 'is_seller':is_seller,'countries':country,'countries_dict':COUNTRY_TRANSLATE }
		
		return self.render_to_response(context)


class SellerHome(TemplateResponseMixin, View):
	template_name = 'core/seller_home.html'		

	def get(self, request, *args, **kwargs):

		tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=request.user.pk, payment__seller_was_rewarded=False)
		revenue_total = 0

		for ticket in tickets_revenue:
			revenue_total += ticket.value

		
		context = {'faturamento': revenue_total}
		return self.render_to_response(context)


class ResetRevenue(View):


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
				'telefone': seller.cellphone,'faturamento': revenue_total, 'status': 200}
			
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
		#print(data)

		return HttpResponse( data, content_type='application/json' )


class BetView(View):

	def post(self, request, *args, **kwargs):

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
			


class BetTicketDetail(TemplateResponseMixin, View):
	template_name = 'core/ticket_details.html'

	def get(self, request, *args, **kwargs):
		ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])


		content = "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
		if ticket.random_user:
			content += "<CENTER> CLIENTE: " + ticket.random_user.first_name + "<BR>"
		else:
			content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"
		content += "<CENTER> APOSTA: R$" + str(ticket.value) + "<BR>"
		content += "<CENTER> GANHO POSSÍVEL: R$" + str(ticket.reward.value) + "<BR>"
		
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
			if not c.game.odds_calculated:
				content += "<RIGHT> Status: Em Aberto"
			else:
				content += "<RIGHT> Status: " + ("Venceu" if c.winning else "Perdeu") + "<BR>"
			
			content += "<CENTER> -------------------------------> <BR>"
		content += "<LEFT> "+ settings.APP_VERBOSE_NAME
		
		content = urllib.parse.urlparse(content).geturl()

		context = {'ticket': ticket, 'print': content, 'valor_apostado': "%.2f" % ticket.value, 'ganho_possivel': "%.2f" % ticket.reward.value}

		return self.render_to_response(context)	


class ValidateTicket(View):

	def post(self, request):
		if not request.POST['ticket']:
			return JsonResponse({'status': 400})

		if request.user.has_perm('core.can_validate_payment'):
			pk = int(request.POST['ticket'])
			ticket_queryset = BetTicket.objects.filter(pk=pk)
			if ticket_queryset.exists():
				can_validate = True
				for cotation in ticket_queryset.first().cotations.all():
					if cotation.game.start_game_date < tzlocal.now():
						can_validate = False
				if can_validate:
					ticket_queryset.first().ticket_valid(request.user)
					return JsonResponse({'status': 200})
				else:
					return JsonResponse({'status': 403})
			else:			
				return JsonResponse({'status': 404})
		else:
			return JsonResponse({'status': 400})


class PunterPayment(View):

	def post(self, request):
		if not request.POST['ticket']:
			return JsonResponse({'status': 400})

		if request.user.has_perm('core.can_reward'):
			pk = int(request.POST['ticket'])
			ticket_queryset = BetTicket.objects.filter(pk=pk)
			if ticket_queryset.exists():
				
				ticket = ticket_queryset.first()
				if ticket.bet_ticket_status == 'Venceu.':
					ticket.reward_payment(request.user)
					return JsonResponse({'status': 200})
				else:
					return JsonResponse({'status': 401})

			else:
				return JsonResponse({'status': 404})
		else:
			return JsonResponse({'status': 400})	


class PayedBets(TemplateResponseMixin,View):
	template_name = 'core/list_bets.html'

	def get(self, request):
		bet_tickets = BetTicket.objects.filter(payment__who_set_payment_id=request.user.id).filter(payment__status_payment='Pago')

		paginator = Paginator(bet_tickets, 10)        
		page = request.GET.get('page')

		context = paginator.get_page(page)

		index = context.number - 1  # edited to something easier without index
		# This value is maximum index of your pages, so the last page - 1
		max_index = len(paginator.page_range)
		# You want a range of 7, so lets calculate where to slice the list
		start_index = index - 3 if index >= 3 else 0
		end_index = index + 3 if index <= max_index - 3 else max_index
		# Get our new page range. In the latest versions of Django page_range returns 
		# an iterator. Thus pass it to list, to make our slice possible again.
		page_range = list(paginator.page_range)[start_index:end_index]		

		return self.render_to_response({'bet_tickets':context, 'page_range':page_range})	

