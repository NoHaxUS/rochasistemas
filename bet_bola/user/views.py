from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import CreateView, FormView
from django.contrib import messages
from .models import Punter
from core.models import Game, Championship, BetTicket
from user.models import Punter
from datetime import datetime
#from django.contrib.auth.models import User
from user.models import CustomUser
import json
# Create your views here.



class PunterHome(TemplateResponseMixin, View):
    template_name = 'user/user_home.html'

    def get(self, request, *args, **kwargs):

        bet_tickets = BetTicket.objects.filter(user=request.user).order_by('-pk')
        change_password_form = PasswordChangeForm(request.user)
        
        paginator = Paginator(bet_tickets, 10)        
        page = request.GET.get('page')

        context = paginator.get_page(page)
        
        index = context.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # Get our new page range. In the latest versions of Django page_range returns 
        # an iterator. Thus pass it to list, to make our slice possible again.
        page_range = list(paginator.page_range)[start_index:end_index]


        return self.render_to_response({'bet_tickets': context,'change_password_form': change_password_form, 'page_range':page_range})


class PunterCreate(View):

    def post(self, request):
        print(request.POST)

        errors = {'errors':False, 'data': []}


        if not request.POST['full_name']:
            errors['errors'] = True
            errors['data'].append('O nome é obrigatório')


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
