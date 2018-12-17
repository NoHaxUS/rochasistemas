from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from core.models import Ticket
from user.models import Punter, CustomUser, Seller, Manager
import utils.timezone as tzlocal
from utils.response import UnicodeJsonResponse
import json


class PunterRegister(View):

    def post(self, request):

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
            if CustomUser.objects.filter(username=request.POST['login']).exists():
                errors['errors'] = True
                errors['data'].append('Esse login já está em uso, desculpe.')
        if request.POST['email']:
            if CustomUser.objects.filter(email=request.POST['email']).exists():
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



class UserLogin(View):

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            data = {
                'success':True,
                'message':'Logado com sucesso'
            }
            
            request.session['ticket'] = {}
            request.session.modified = True

            return UnicodeJsonResponse(data)
        else:
            data = {
                'success':False,
                'message':'Login ou senha inválidos'
            }
            return UnicodeJsonResponse(data)


class UserLogout(View):
    """
    Provides users the ability to logout
    """
    
    def get(self, request, *args, **kwargs):
        logout(request)
        response = redirect('core:core_home')
        response.delete_cookie('ticket_cookie')
        return response

