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
from user.forms.create_punter_form import CreatePunterForm
from user.models import Punter,Seller
from .forms import BetTicketForm
from django.core import serializers
import json

#import pdb; pdb.set_trace()
# Create your views here.

class Home(TemplateResponseMixin, View):
	template_name = 'core/index.html'	
	form = AuthenticationForm()
	form_punter = CreatePunterForm()
	games = Game.objects.able_games()

	def get(self, request, *args, **kwargs):
		championships = list()

		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
		
		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'games': self.games ,'championships': championships,'form': self.form, 'form_punter': self.form_punter, 'is_seller':is_seller}
		
		return self.render_to_response(context)



class GameChampionship(TemplateResponseMixin, View):
	template_name = 'core/index.html'	
	form = AuthenticationForm()
	form_punter = CreatePunterForm()


	def get(self, request, *args, **kwargs):
		championships = list()

		for i in Championship.objects.all():
			if i.my_games.able_games().count() > 0:
				championships.append(i)
				

		championship = Championship.objects.get( pk=int(self.kwargs["pk"]) )
		games = Game.objects.able_games().filter(championship=championship)
	
		is_seller = None
		if request.user.is_authenticated:
			try:
				seller = Seller.objects.get(pk=int(request.user.pk))
				is_seller = seller.is_seller()
			except Seller.DoesNotExist:
				is_seller = False

		context = {'games': games ,'championships': championships,'form': self.form, 'form_punter': self.form_punter, 'is_seller':is_seller}
		
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

			ticket = BetTicket(
				punter=Punter.objects.get(pk=request.user.pk), 
				seller=None,
				value=float(request.POST['ticket_value']), 
				payment=Payment.objects.create(), 
				reward=Reward.objects.create())
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
				ticket.reward.value = cotation_sum * float(request.POST['ticket_value'])
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


class Validar(View):

	def post(self, request):
		if request.user.has_perm('core.can_validate_payment'):
			pk = int(request.POST['ticket'])
			if pk in [ticket.pk for ticket in BetTicket.objects.all()]:
				ticket = BetTicket.objects.get(pk = pk)
				ticket.ticket_valid(request.user)
				return HttpResponse("<h1>Ticket Validate</h1>")
			else:			
				return HttpResponse("<h1>There's no such a ticket</h1>")	
		else:
			return HttpResponse("<h1>User has not permission </h1>")	


class PunterPayment(View):

	def post(self, request):		
		if request.user.has_perm('core.can_reward'):
			pk = int(request.POST['ticket'])
			if pk in [ticket.pk for ticket in BetTicket.objects.all()]:
				ticket = BetTicket.objects.get(pk = pk)
				ticket.reward_payment(request.user)
				return HttpResponse("<h1>Payment paid</h1>")
			else:
				return HttpResponse("<h1>There's no such a betticket</h1>")
		else:
			return HttpResponse("<h1>User has not permission </h1>")	