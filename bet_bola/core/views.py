from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.utils import timezone
from django import forms
from datetime import datetime
from core.models import BetTicket,Bet,Game
# Create your views here.

class Home(View):

    def get(self, request, *args, **kargs):
        return HttpResponse("OK")

class BetTicketForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		#self.bets = kwargs.pop('bets')
		super(BetTicketForm, self).__init__(*args, **kwargs)			
		self.fields.__setitem__('bets',forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=([(bet.pk, bet) for bet in Bet.objects.all()])))

	def get_form_kwargs(self):
		# pass "user" keyword argument with the current user to your form
		kwargs = super(BetTicketForm, self).get_form_kwargs()
		print(kwargs)
		kwargs['user'] = self.request.user
		kwargs['creation_date'] = datetime.now()
		return kwargs

	class Meta:
		model = BetTicket
		fields = '__all__'
		exclude = ['punter','seller','creation_date','reward']

class BetTicketCreate(CreateView):	
	form_class = BetTicketForm
	template_name = 'betticket_form.html'	
	success_url="home"

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(BetTicketCreate, self).get_context_data(**kwargs)
		context['bets']=Bet.objects.all()
		return context


class GameListView(ListView):
	model = Game
	template_name = 'game_list.html'	

	def get_context_data(self, **kwargs):
		context = super(GameListView, self).get_context_data(**kwargs)
		context['now'] = timezone.now()
		return context