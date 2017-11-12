from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.views.generic.edit import CreateView
from .models import Punter
# Create your views here.



class PunterCreate(CreateView):	
	model = Punter
	fields = ['first_name','last_name','username','password','email','date_joined','birthday']	
	template_name = 'core/punter_form.html'
	#success_url = 'core/login'#todo

	def form_valid(self, form):
		obj = form.save(commit=False)		
		obj.set_password(self.request.POST['password'])#obj.created_by = self.request.user
		obj.save()        
		return super(PunterCreate, self).form_valid(form)

	def get_success_url(self):
		return reverse('login')


class Login(View):
	def post(self, request):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			print("DEU RUUUUUUUUIM")
			return redirect('game_list_view')
		else:		
			return HttpResponse("<h1>LOGIN ERROR</h1>")

	def get(self, request):
		form = AuthenticationForm()
		return render(request, "user/index.html", {'form':form})

