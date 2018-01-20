from django.shortcuts import render,reverse,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward
from user.models import Punter,Seller
from .forms import BetTicketForm
from django.core import serializers
from django.conf import settings
from user.models import CustomUser, RandomUser
import json
import urllib

#import pdb; pdb.set_trace()
# Create your views here.

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
	dict_championship_games = {}


	def get(self, request, *args, **kwargs):
		championships = list()
		country = list()
		
		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.my_games.today_able_games().count() > 0:
					self.dict_championship_games[i] = Game.objects.today_able_games().filter(championship=i)				
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
		
		total_value = 10
		context = {'faturamento': total_value}
		return self.render_to_response(context)


class ResetRevenue(View):
	
	def post(self, request, *args, **kwargs):
		return HttpResponse('OK')



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
		#return HttpResponse(request.POST['game_id'])
		#request.session.flush()
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
					


			if ticket_bet_value <= 0:
				return JsonResponse({'status':400})

	
			ticket = BetTicket(
				user=CustomUser.objects.get(pk=request.user.pk),
				value=ticket_bet_value,
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None),				
				)

				
			cotation_sum = 1
			game_cotations = []
			for game_id in request.session['ticket']:
				game_contation = None
				try:
					game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
					game_cotations.append(game_contation)
					cotation_sum *= game_contation.value
				except Cotation.DoesNotExist:
					return JsonResponse({'status':400})
			
			ticket_reward_value = round(cotation_sum * ticket_bet_value ,2)
			if float(ticket_reward_value) > float(settings.MAX_REWARD):
				return JsonResponse({'status':406}) # NOT ACEPTED

			elif len(game_cotations) < settings.MIN_BET_PER_TICKET:
				return JsonResponse({'status':417}) # EXPECTATION FAILED
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


		date = str(ticket.creation_date.date().day) + "/" + str(ticket.creation_date.date().month) + "/" + str(ticket.creation_date.date().year)

		content = "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
		content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

		#if ticket.seller != None:
		#	content += "<CENTER> COLABORADOR: " + ticket.seller.first_name

		content += "<CENTER> DATA: " + date
		content += "<BR><BR>"

		content += "<LEFT> APOSTAS <BR>"
		content += "<CENTER>----------------------------------------------- <BR>"

		for c in ticket.cotations.all():
			content += "<LEFT>" + c.game.name + "<BR>"
			game_date = str(c.game.start_game_date.date().day) +"/"+str(c.game.start_game_date.date().month)+"/"+str(c.game.start_game_date.date().day)+ " " +str(c.game.start_game_date.hour)+":"+str(c.game.start_game_date.minute)
			content += "<LEFT>" + game_date + "<BR>"
			content += "<LEFT>"+ c.kind + "<BR>"
			content += "<LEFT>" + c.name + " --> " + str(c.value) + "<BR>"

			if c.game.odds_calculated:
				content += "<RIGHT> Status: Em Aberto"
			else:
				content += "<RIGHT> Status: Fechado - " + ("Venceu" if c.winning else "Perdeu") + "<BR>"
			
			content += "<CENTER> ----------------------------------------------- <BR>"
			content += "<CENTER> BET BOLA"
		
		content = urllib.parse.quote_plus(content)

		context = {'ticket': ticket, 'print': content}

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
					if cotation.game.start_game_date < timezone.now():
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