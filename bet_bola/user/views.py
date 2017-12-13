from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView, FormView
from django.contrib import messages
from .forms.create_punter_form import CreatePunterForm
from .models import Punter
from core.models import Game, Championship, BetTicket
from user.models import Punter
from datetime import datetime
# Create your views here.


class PunterChangePass(TemplateResponseMixin, View):
    template_name = 'user/user_change_pass.html'

    def get(self, request, *args, **kwargs):
        #bet_tickets = BetTicket.objects.filter(punter=request.user)
        return self.render_to_response({})


class PunterHome(TemplateResponseMixin, View):
    template_name = 'user/user_home.html'

    def get(self, request, *args, **kwargs):
        bet_tickets = BetTicket.objects.filter(user=request.user)
        change_password_form = PasswordChangeForm(request.user)
        context = list()
        for i in range(len(bet_tickets)-1, -1,-1):
            context.append(bet_tickets[i])


        return self.render_to_response({'bet_tickets': context,'change_password_form': change_password_form})


class PunterCreate(FormView):
    form_class = CreatePunterForm
    template_name = 'core/index.html'
    success_url = '/'

    def form_valid(self, form):
        punter = form.save(commit=False)
        punter.date_joined = datetime.now()
        punter.save()
        return super(PunterCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        form = AuthenticationForm()
        form_punter = CreatePunterForm()
        championships = Championship.objects.all()
        games = Game.objects.able_games()

        context = {'games': games, 'championships': championships,
                   'form': form, 'form_punter': form_punter}
        return context

    def form_invalid(self, form):
        # help(form.errors)
        erros = ""
        for i in form.errors.keys():
            erros += form.errors[i]

        messages.info(
            self.request,
            erros
        )
        
        return super(PunterCreate, self).form_invalid(form)



class Login(View):

    def get(self, request):
        form = AuthenticationForm()
        return render(request, "user/index.html", {'form': form})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if(request.user.pk in [user.pk for user in Punter.objects.all()]):
                return redirect('core:home')
            else:
                return redirect('core:seller_home')
        else:
            return HttpResponseRedirect('/#/login_error')


class Logout(View):
    """
    Provides users the ability to logout
    """

    def get(self, request, *args, **kwargs):
        logout(request)
        response = redirect('core:home')
        response.delete_cookie('ticket_cookie')
        return response


class PasswordChange(View):
    """
    Provides users the ability to logout
    """

    def post(self, request, *args, **kwargs):

        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)#this line makes the user log in automatically, after the password change
            #messages.success(request, 'Your password was successfully updated!') WE HAVE TO TAKE A LOOK ON THIS METHOD MESSAGE
            response = redirect('core:home')
            response.delete_cookie('ticket_cookie')            
            return response
        else:
            pass
            #messages.error(request, 'Please correct the error below.')
