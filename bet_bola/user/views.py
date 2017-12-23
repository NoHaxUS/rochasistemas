from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView, FormView
from django.contrib import messages
from .forms.create_punter_form import CreatePunterForm
from .models import Punter
from core.models import Game, Championship, BetTicket
from user.models import Punter
from datetime import datetime
from django.contrib.auth.models import User
import json
# Create your views here.



class PunterHome(TemplateResponseMixin, View):
    template_name = 'user/user_home.html'

    def get(self, request, *args, **kwargs):
        bet_tickets = BetTicket.objects.filter(user=request.user)
        change_password_form = PasswordChangeForm(request.user)
        context = list()
        for i in range(len(bet_tickets)-1, -1,-1):
            context.append(bet_tickets[i])


        return self.render_to_response({'bet_tickets': context,'change_password_form': change_password_form})


class PunterCreate(View):

    def post(self, request):
        print(request.POST)

        errors = {'errors':False, 'data': []}


        if not request.POST['full_name']:
            errors['errors'] = True
            errors['data'].append('O nome é obrigatório')

        elif not request.POST['email']:
            errors['errors'] = True
            errors['data'].append('O email é obrigatório')

        elif not request.POST['login']:
            errors['errors'] = True
            errors['data'].append('O login é obrigatório')

        elif not request.POST['password']:
            errors['errors'] = True
            errors['data'].append('A senha é obrigatória')

        elif not request.POST['cellphone']:
            errors['errors'] = True
            errors['data'].append('O Telefone é obrigatório')

        if request.POST['login']:
            if Punter.objects.filter(username=request.POST['login']).exists():
                errors['errors'] = True
                errors['data'].append('Esse login já está em uso, desculpe.')

        if request.POST['email']:
            if Punter.objects.filter(email=request.POST['email']).exists():
                errors['errors'] = True
                errors['data'].append('Esse email já está em uso, desculpe.')

        
        if errors['errors']:
            return HttpResponse(json.dumps(errors, ensure_ascii=False), content_type="application/json", status=406)
        else:
            punter = Punter(first_name=request.POST['full_name'],
            email=request.POST['email'],
            username=request.POST['login'],
            password=request.POST['password'],
            cellphone=request.POST['cellphone'])
            punter.save()

            user = authenticate(username=request.POST['login'], password=request.POST['password'])
            print(user)
            if user is not None:
                login(request, user)
                return HttpResponse("User Created")


class Login(View):

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if(request.user.pk in [user.pk for user in Punter.objects.all()]):
                return HttpResponseRedirect('/#/login_ok')
            else:
                #return redirect('core:seller_home')
                return HttpResponseRedirect('/#/login_ok')
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
    Provides users change password
    """

    def post(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            actual_pass = request.POST['actual_pass']
            new_pass = request.POST['new_pass']

            print(request.user)
            
            if request.user.check_password(actual_pass):
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)

                return JsonResponse({"status":200})
            else:
                return JsonResponse({"status":406})
