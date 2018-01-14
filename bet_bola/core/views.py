from django.shortcuts import render,reverse,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from .models import Cotation,BetTicket,Game,Championship,Payment,Reward
from user.models import Punter,Seller
from .forms import BetTicketForm
from django.core import serializers
#from django.contrib.auth.models import User
from user.models import CustomUser
import json

#import pdb; pdb.set_trace()
# Create your views here.

class Home(TemplateResponseMixin, View):
	template_name = 'core/index.html'
	games = Game.objects.able_games()


	def get(self, request, *args, **kwargs):
		championships = list()
		country = list()
		
		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				if i.country not in country:					
					country.append(i.country)

		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'games': self.games ,'championships': championships, 'is_seller':is_seller,'countries':country}
		

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

		context = {'games': games ,'championships': championships,'form': self.form, 'is_seller':is_seller,'countries':country}
		
		return self.render_to_response(context)


class SellerHome(TemplateResponseMixin, View):
	template_name = 'core/seller_home.html'		

	def get(self, request, *args, **kwargs):				
		context = {}
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
		return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


class CreateTicketView(View):
	def post(self, request, *args, **kwargs):
		

		if request.user.is_authenticated:
			if 'ticket' not in request.session:
				return JsonResponse({'status':403})

			if request.POST.get('ticket_value') == '':
				return JsonResponse({'status':400})
			
			#ticket_bet_value = float( request.POST.get('ticket_value') )
			ticket_bet_value = 2

			if ticket_bet_value <= 0:
				return JsonResponse({'status':400})
			
			#print(request.POST.get('ticket_value'))

			ticket = BetTicket(
				user=CustomUser.objects.get(pk=request.user.pk), 
				seller=None,
				value=ticket_bet_value,
				payment=Payment.objects.create(payment_date=None), 
				reward=Reward.objects.create(reward_date=None)
				)
			ticket.save()

			
			cotation_sum = 1
			for game_id in request.session['ticket']:
				game_contation = None
				try:
					game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
					cotation_sum *= game_contation.value
				except Cotation.DoesNotExist:
					return JsonResponse({'status':400})

				ticket.cotations.add( game_contation )
				ticket.reward.value = cotation_sum * ticket_bet_value
				ticket.reward.save()
			return JsonResponse({'ticket_pk': ticket.pk ,'status':201})

		else:
			return JsonResponse({'status':401})
			


class BetTicketDetail(TemplateResponseMixin, View):
	template_name = 'core/ticket_details.html'

	def get(self, request, *args, **kwargs):
		ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])
		context = {'ticket': ticket}
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