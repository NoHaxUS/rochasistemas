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
from datetime import datetime
from .models import Cotation,BetTicket,Game,Championship
from user.models import Punter
from .forms import BetTicketForm
# Create your views here.

class Home(TemplateResponseMixin, View):
	template_name = 'core/index.html'	
	form = AuthenticationForm()
	championships = Championship.objects.all()
	games = Game.objects.filter( Q(status_game="NS")| Q(status_game="LIVE") | Q(status_game="HT") | Q(status_game="ET") 
		| Q(status_game="PT") | Q(status_game="BREAK") | Q(status_game="DELAYED"))

	def get(self, request, *args, **kwargs):				
		context = {'games': self.games ,'championships': self.championships,'form': self.form}
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)						
			context = {'games': self.games ,'championships': self.championships,'user': request.user}
			return self.render_to_response(context)
		else:		
			return HttpResponse("<h1>LOGIN ERROR</h1>")

class AddBetToTicket(View):

	def post(self, request, *args, **kwargs):

		request.session.flush()
		if 'ticket' not in request.session:
			request.session['ticket'] = []
			pk = self.kwargs["pk"]
			request.session['ticket'].append( int(pk) )
			
			response = HttpResponse()
			response.status_code = 201
			return response
		else:
			pk = self.kwargs["pk"]
			request.session['ticket'].append( int(pk) )
			response = HttpResponse()
			response.status_code = 201
			return response

	def get(self, request, *args, **kwargs):
		if not request.session['ticket']:
			return HttpResponse("Empty")
		else:

			return JsonResponse({'ticket': request.session['ticket']})


class GameChampionship(Home):
	def get(self, request, *args, **kwargs):
		championship = get_object_or_404(Championship, pk=self.kwargs["pk"])		
		self.games = Game.objects.filter( (Q(status_game="NS")| Q(status_game="LIVE") | Q(status_game="HT") | Q(status_game="ET") 
		| Q(status_game="PT") | Q(status_game="BREAK") | Q(status_game="DELAYED")) & Q(championship=championship))
		return super(GameChampionship, self).get(self, request, *args, **kwargs)


class Logout(View):
    """
    Provides users the ability to logout
    """    
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('home')


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