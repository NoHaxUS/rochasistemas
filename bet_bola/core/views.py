from django.shortcuts import render,reverse
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
from .models import Cotation,BetTicket,Game,Championship
from user.models import Punter
from .forms import BetTicketForm
# Create your views here.

class Home(View):

    def get(self, request, *args, **kargs):
        return HttpResponse("OK")


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

class GameListView(ListView):
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