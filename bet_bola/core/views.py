from django.shortcuts import render,reverse,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from .models import Cotation,BetTicket,Game,Championship
from user.forms.create_punter_form import CreatePunterForm
from user.models import Punter
from .forms import BetTicketForm
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


class GameChampionship(Home):
	def get(self, request, *args, **kwargs):
		championship = get_object_or_404(Championship, pk=self.kwargs["pk"])		
		self.games = Game.objects.able_games().filter(championship = championship)
		return super(GameChampionship, self).get(self, request, *args, **kwargs)


class BetTicketCreate(CreateView):	
	form_class = BetTicketForm
	template_name = 'core/betticket_form.html'		

	def get_success_url(self):
		return reverse('home')

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(BetTicketCreate, self).get_context_data(**kwargs)
		context['cotations']=Cotation.objects.all()
		return context

	def form_valid(self, form):        
		form.instance.punter = Punter.objects.get(user_ptr=self.request.user.pk)
		form.instance.creation_date = datetime.now()
		return super(BetTicketCreate, self).form_valid(form)

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
