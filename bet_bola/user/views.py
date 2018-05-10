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
from guardian.shortcuts import get_objects_for_user
from core.models import BetTicket
from user.models import Punter, CustomUser, Seller, Manager
import utils.timezone as tzlocal
from utils.response import UnicodeJsonResponse
import json


class PunterHome(LoginRequiredMixin, TemplateResponseMixin, View):

    template_name = 'user/punter_home.html'
    login_url = reverse_lazy('core:core_home')

    def get(self, request, *args, **kwargs):

        bet_tickets = BetTicket.objects.filter(user=request.user).order_by('-pk')
        change_password_form = PasswordChangeForm(request.user)
        paginator = Paginator(bet_tickets, 10)        
        page = request.GET.get('page')
        context = paginator.get_page(page)
        index = context.number - 1  
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        return self.render_to_response({'bet_tickets': context,'change_password_form': change_password_form, 'page_range':page_range})


class GetSellersByManager(PermissionRequiredMixin, TemplateResponseMixin, View):

    permission_required = 'user.is_superuser'
    template_name = 'user/sellers_by_manager.html'
    raise_exception = True

    def get(self, request, *args, **kwargs):

        manager_id =  kwargs['manager_id']
        
        manager = CustomUser.objects.get(pk=manager_id)
        sellers = get_objects_for_user(manager, 'user.set_credit_limit').order_by('-pk')

        paginator = Paginator(sellers, 10)        
        page = request.GET.get('page')
        context = paginator.get_page(page)
        index = context.number - 1  
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]

        return self.render_to_response({'sellers': context, 'page_range':page_range})


class ManagerHome(PermissionRequiredMixin,TemplateResponseMixin, View):
    permission_required = 'user.be_manager'
    template_name = 'user/manager_panel.html'
    raise_exception = True

    def get(self, request, *args, **kwargs):        
        return self.render_to_response({})


class ManagerSellers(PermissionRequiredMixin, TemplateResponseMixin, View):

    permission_required = 'user.be_manager'
    template_name = 'user/manager_sellers.html'
    raise_exception = True

    def get(self, request, *args, **kwargs):

        sellers = get_objects_for_user(request.user, 'user.set_credit_limit').order_by('-pk')   

        paginator = Paginator(sellers, 10)        
        page = request.GET.get('page')
        context = paginator.get_page(page)
        index = context.number - 1  
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]

        return self.render_to_response({'sellers': context, 'page_range':page_range })


class SellerValidateTicket(PermissionRequiredMixin, View):

    permission_required = 'user.be_seller'
    raise_exception = True

    def post(self, request):

        if not request.POST['ticket']:
            return JsonResponse({'status': 400})

        pk = int(request.POST['ticket'])
        ticket_queryset = BetTicket.objects.filter(pk=pk)
        if ticket_queryset.exists():
            can_validate = True
            for cotation in ticket_queryset.first().cotations.all():
                if cotation.game.start_game_date < tzlocal.now():
                    can_validate = False
            if can_validate:
                if ticket_queryset.first().payment.status_payment == 'Pago':
                    return JsonResponse({'status': 406})
                else:
                    if not ticket_queryset.first().validate_ticket(request.user):
                        return JsonResponse({'status': 405})
                    return JsonResponse({'status': 200})

            else:
                return JsonResponse({'status': 403})
        else:			
            return JsonResponse({'status': 404})


class SellerPayPunter(PermissionRequiredMixin, View):


    permission_required = 'user.be_seller'
    raise_exception = True

    def post(self, request):

        if not request.POST['ticket']:
            return JsonResponse({'status': 400})

        pk = int(request.POST['ticket'])
        ticket_queryset = BetTicket.objects.filter(pk=pk)
        if ticket_queryset.exists():
            
            ticket = ticket_queryset.first()
            if ticket.bet_ticket_status == 'Venceu':
                ticket.reward_ticket(request.user)
                return JsonResponse({'status': 200})
            else:
                return JsonResponse({'status': 401})
        else:
            return JsonResponse({'status': 404})

class SellerPayedBets(PermissionRequiredMixin, TemplateResponseMixin, View):

    template_name = 'user/seller_payed_bets.html'
    permission_required = 'user.be_seller'
    login_url = reverse_lazy('core:core_home')

    def get(self, request):
        bet_tickets = BetTicket.objects.filter(payment__who_set_payment_id=request.user.id).filter(payment__status_payment='Pago').order_by('-pk')

        paginator = Paginator(bet_tickets, 10)        
        page = request.GET.get('page')
        context = paginator.get_page(page)
        index = context.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index

        page_range = list(paginator.page_range)[start_index:end_index]		

        return self.render_to_response({'bet_tickets':context, 'page_range':page_range})	


class SellerCreatedBets(PermissionRequiredMixin, TemplateResponseMixin, View):

    template_name = 'user/seller_created_bets.html'
    permission_required = 'user.be_seller'
    login_url = reverse_lazy('core:core_home')

    def get(self, request):
        bet_tickets = BetTicket.objects.filter(user=request.user.id).order_by('-pk')

        paginator = Paginator(bet_tickets, 10)        
        page = request.GET.get('page')
        context = paginator.get_page(page)
        index = context.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index

        page_range = list(paginator.page_range)[start_index:end_index]		

        return self.render_to_response({'bet_tickets':context, 'page_range':page_range})	


class SellerHome(LoginRequiredMixin, PermissionRequiredMixin, TemplateResponseMixin, View):
    
    template_name = 'user/seller_home.html'
    permission_required = 'user.be_seller'
    login_url = reverse_lazy('core:core_home')

    def get(self, request, *args, **kwargs):

        tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=request.user.pk, payment__seller_was_rewarded=False)
        revenue_total = 0

        for ticket in tickets_revenue:
            revenue_total += ticket.value

        context = {'faturamento': "%.2f" % revenue_total}
        return self.render_to_response(context)


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


class SellerRegister(View):

    def post(self, request):

        errors = {'errors':False, 'data': []}
        if not request.POST['full_name']:
            errors['errors'] = True
            errors['data'].append('O nome é obrigatório')
        elif not request.POST['cpf']:
            errors['errors'] = True
            errors['data'].append('O cpf é obrigatório')
        elif not request.POST['login']:
            errors['errors'] = True
            errors['data'].append('O login é obrigatório')
        elif not request.POST['password']:
            errors['errors'] = True
            errors['data'].append('A senha é obrigatória')
        elif not request.POST['cellphone']:
            errors['errors'] = True
            errors['data'].append('O Telefone é obrigatório')
        elif not request.POST['address']:
            errors['errors'] = True
            errors['data'].append('O endereço é obrigatório')

        if request.POST['login']:
            if Seller.objects.filter(username=request.POST['login']).exists():                
                errors['errors'] = True
                errors['data'].append('Esse login já está em uso, desculpe.')
        if request.POST['email']:
            if Seller.objects.filter(email=request.POST['email']).exists():
                errors['errors'] = True
                errors['data'].append('Esse email já está em uso, desculpe.')

        if errors['errors']:
            return HttpResponse(json.dumps(errors, ensure_ascii=False), content_type="application/json", status=406)
        else:
            seller = Seller(first_name=request.POST['full_name'],
            cpf=request.POST['cpf'],
            email=request.POST['email'],
            username=request.POST['login'],
            password=request.POST['password'],
            address=request.POST['address'],
            cellphone=request.POST['cellphone'])
            seller.save()            
                    
            if request.user.has_perm('user.be_manager'):
                sellers = [seller]
                request.user.manager.add_set_limit_permission(sellers)
                return HttpResponse("Seller Created")


class ManagerTransferCredit(PermissionRequiredMixin, View):

    permission_required = 'user.be_manager'
    raise_exception = True

    def post(self, request):       
        manager = Manager.objects.get(pk=request.user.pk)        
        seller = Seller.objects.get(pk=request.POST['seller'])        
        valor = float(request.POST['valor'])
        message = manager.transfer_credit_limit(seller,valor)     
        return UnicodeJsonResponse({'message':message})


class ManagerPermissions(LoginRequiredMixin, PermissionRequiredMixin, TemplateResponseMixin, View):
    template_name = 'user/manager_permissions.html'
    permission_required = 'user.is_superuser'
    login_url = reverse_lazy('core:core_home')

    def get(self, request, *args, **kwargs):

        managers = Manager.objects.all()       
        paginator = Paginator(managers, 10)        
        page = request.GET.get('page')
        context = paginator.get_page(page)
        index = context.number - 1  
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]

        return self.render_to_response({'gerentes': context, 'page_range':page_range})

    def post(self, request):                    

        manager = Manager.objects.get(pk=request.POST['gerente'])
        message = 'Gerente ' + manager.first_name
        sellers = []        

        for quant in range(int(request.POST['quantidade'])):
            username = request.POST['vendedor'+str(quant+1)]            
            
            if not Seller.objects.filter(username=username).exists():
                return UnicodeJsonResponse({'message':'Usuario '+ username + ' não existe, selecione usuarios existentes'})

            sellers.append(Seller.objects.get(username=username))
            

            if quant == 0:
                message += ' recebeu permissão ao vendedor ' + sellers[quant].first_name
            else:
                message += ' e ' + sellers[quant].first_name
            
        
        manager.add_set_limit_permission(sellers)        
        
        return UnicodeJsonResponse({'message':message})


    def delete(self, request):

        from django.http import QueryDict
        delete = QueryDict(request.body)

        print(delete)

        manager = Manager.objects.get(pk=delete['gerente']) 
        message = 'Permissão de adicionar credito do gerente ' + manager.username
        sellers = []

        for quant in range(int(delete['quantidade'])):
            username = delete['vendedor'+str(quant+1)]            
            
            if not Seller.objects.filter(username=username).exists():
                return UnicodeJsonResponse({'message':'Usuario '+ username + ' não existe, selecione usuarios existentes'})

            sellers.append(Seller.objects.get(username=username))
            

            if manager.has_perm('set_credit_limit', Seller.objects.get(username=username)):
                if quant == 0:
                    message += ' foi revogada no vendedor ' + sellers[quant].first_name
                else:
                    message += ' e ' + sellers[quant].first_name    
            else:
                return UnicodeJsonResponse({'message':'Gerente '+ manager.username + ' não tem permissão ao usuario ' + username})

        manager.remove_set_limit_permission(sellers)        
        
        
        return UnicodeJsonResponse({'message':message})





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


class UserPasswordChange(View):
    """
    Provides users change password
    """

    def post(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            actual_pass = request.POST['actual_pass']
            new_pass = request.POST['new_pass']
            
            if request.user.check_password(actual_pass):
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)

                return JsonResponse({"status":200})
            else:
                return JsonResponse({"status":406})
