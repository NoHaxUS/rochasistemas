from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView,FormView
from .forms.create_punter_form import CreatePunterForm
from .models import Punter
from core.models import Game,Championship,BetTicket
# Create your views here.

class PunterChangePass(TemplateResponseMixin, View):
	template_name = 'user/user_change_pass.html'
	
	def get(self, request, *args, **kwargs):
		#bet_tickets = BetTicket.objects.filter(punter=request.user)
		return self.render_to_response({})

class PunterHome(TemplateResponseMixin, View):
	template_name = 'user/user_home.html'
	
	def get(self, request, *args, **kwargs):
		bet_tickets = BetTicket.objects.filter(punter=request.user)
		return self.render_to_response({'bet_tickets': bet_tickets})

class PunterCreate(FormView):	
	form_class = CreatePunterForm
	template_name = 'core/index.html'
	success_url = '/'	

	def form_valid(self, form):
		obj = form.save(commit=False)		
		obj.set_password(self.request.POST['password'])
		obj.save()        
		return super(PunterCreate, self).form_valid(form)

	def get_context_data(self, **kwargs):
		form = AuthenticationForm()		
		form_punter = CreatePunterForm()
		championships = Championship.objects.all()
		games = Game.objects.able_games()
        
		context = {'games': games ,'championships': championships,'form': form, 'form_punter': form_punter}
		return context


class Login(View):
	
	def get(self, request):
		form = AuthenticationForm()
		return render(request, "user/index.html", {'form':form})

	def post(self, request):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)			
			return redirect('core:home')
		else:		
			return HttpResponse("<h1>LOGIN ERROR</h1>")

class Logout(View):
    """
    Provides users the ability to logout
    """    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('core:home')
