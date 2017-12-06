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
from user.models import Punter
from .forms import BetTicketForm
from django.core import serializers

#import pdb; pdb.set_trace()
# Create your views here.

class Home(TemplateResponseMixin, View):
	template_name = 'core/index.html'	
	form = AuthenticationForm()
	form_punter = CreatePunterForm()
	championships = Championship.objects.all()
	games = Game.objects.able_games()

	def get(self, request, *args, **kwargs):				
		context = {'games': self.games ,'championships': self.championships,'form': self.form, 'form_punter': self.form_punter}
		return self.render_to_response(context)


class SellerHome(TemplateResponseMixin, View):
	template_name = 'core/seller_home.html'		

	def get(self, request, *args, **kwargs):				
		context = {}
		return self.render_to_response(context)

class CotationsView(View):
	
	def get(self, request, *args, **kwargs):
		gameid = self.kwargs['gameid']
		return HttpResponse( serializers.serialize("json", Cotation.objects.filter(game_id=gameid, is_standard=False)), content_type='application/json' )


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

			ticket = BetTicket(punter=Punter.objects.get(pk=request.user.pk), seller=None, 
			payment=Payment.objects.create(), 
			reward=Reward.objects.create(value=100), 
			value=int(request.POST['ticket_value']) )
			ticket.save()

			

			for game_id in request.session['ticket']:
				game_contation = None
				try:
					game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
					#game_contation = Cotation.objects.get(pk=int(999999))
				except Cotation.DoesNotExist:
					return JsonResponse({'status':400})

				ticket.cotations.add( game_contation )

	
			#return HttpResponseRedirect('/user')
			return JsonResponse({'status':201})
		else:
			return JsonResponse({'status':401})
			
		

class GameChampionship(Home):
	def get(self, request, *args, **kwargs):
		championship = get_object_or_404(Championship, pk=self.kwargs["pk"])		
		self.games = Game.objects.able_games().filter(championship = championship)
		return super(GameChampionship, self).get(self, request, *args, **kwargs)


class BetTicketDetail(TemplateResponseMixin, View):
	template_name = 'core/ticket_details.html'

	def get(self, request, *args, **kwargs):
		ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])
		context = {'ticket': ticket}
		return self.render_to_response(context)	


class GameListView(ListView):
	login_url='user/championship/'
	redirect_field_name = 'redirect_to'
	queryset = Game.objects.able_games()
	model = Game
	template_name = 'core/game_list.html'	


class ChampionshipListView(ListView):
	model = Championship
	template_name = 'core/championship_list.html'	


class Validar(View):
	
	def get(self, request):
		pass

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
	
	def get(self, request):
		pass

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