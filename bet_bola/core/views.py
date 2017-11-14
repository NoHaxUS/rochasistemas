from django.shortcuts import render,reverse
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from .models import Cotation,BetTicket,Game,Championship
from user.models import Punter
from .forms import BetTicketForm
from django.views.generic.base import TemplateResponseMixin
# Create your views here.

class Home(TemplateResponseMixin, View):
	template_name = 'core/index.html'

	def get(self, request, *args, **kwargs):
		championships = Championship.objects.all()
		games = Game.objects.filter( Q(status_game="NS")| Q(status_game="LIVE") | Q(status_game="HT") | Q(status_game="ET") 
		| Q(status_game="PT") | Q(status_game="BREAK") | Q(status_game="DELAYED"))

		context = {'games': games ,'championships': championships}
		return self.render_to_response(context)


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


class GameListView(ListView,LoginRequiredMixin):
	login_url='user/championship/'
	redirect_field_name = 'redirect_to'
	queryset = Game.objects.filter(Q(status_game="NS")| Q(status_game="LIVE") | Q(status_game="HT") | Q(status_game="ET")
		| Q(status_game="PT") | Q(status_game="BREAK") | Q(status_game="DELAYED"))
	model = Game
	template_name = 'core/game_list.html'	

	def get_context_data(self, **kwargs):
		context = super(GameListView, self).get_context_data(**kwargs)
		context['now'] = timezone.now()
		return context


class ChampionshipListView(ListView):
	model = Championship
	template_name = 'core/championship_list.html'	

	def get_context_data(self, **kwargs):
		context = super(ChampionshipListView, self).get_context_data(**kwargs)
		context['now'] = timezone.now()
		return context