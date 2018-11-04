from django.shortcuts import redirect
from django.views import View
from django.core.paginator import Paginator
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.core import serializers
from django.conf import settings
from .models import Cotation,Ticket,Game, Market,League,Payment,Reward,Location,CotationHistory
from django.db.models import Prefetch, Count
from django.utils import timezone
from django.db.models import Q
from user.models import Seller
from user.models import CustomUser, NormalUser
import utils.timezone as tzlocal
from utils.response import UnicodeJsonResponse
import json
import urllib
from decimal import Decimal
from math import ceil
from  collections import defaultdict

def get_main_menu():

    games = Game.objects.filter(start_date__gt=tzlocal.now(),
    league__isnull=False,
    game_status=1,
    is_visible=True)\
    .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
    .order_by('-league__location__priority', '-league__priority')


    location_leagues = defaultdict(set)

    for game in games:
        if game.league.location:
            location_leagues[game.league.location].add(game.league)
    return location_leagues

class TodayGames(TemplateResponseMixin, View):

    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        
        
        
        page = int(request.GET.get('page')) if request.GET.get('page') else 1

        results_per_page = 80
        start_offset = 0 if page == 1 else (page * results_per_page) - results_per_page
        end_offset = (page * results_per_page)
        
        after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)
        my_qs = Cotation.objects.filter(market__name="1X2")
        
        games = Game.objects.filter(start_date__gt=tzlocal.now(), 
        start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
        game_status=1, 
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .order_by('-league__location__priority','-league__priority')[start_offset:end_offset]


        games_total = Game.objects.filter(start_date__gt=tzlocal.now(), 
        start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
        game_status=1, 
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .count()
        
        num_of_pages =  ceil(games_total / results_per_page)

        league_games = defaultdict(list)
        location_leagues = get_main_menu()
        
        for game in games:
            league_games[game.league].append(game)
        
        context = {'league_games': league_games, 
            'location_leagues': location_leagues,
            'after_tommorrow': after_tommorrow,
            'range_pages': range(1, num_of_pages + 1),
            'current_page': page}
        
        return self.render_to_response(context)

class TomorrowGames(TemplateResponseMixin, View):

    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):

        page = int(request.GET.get('page')) if request.GET.get('page') else 1

        results_per_page = 80
        start_offset = 0 if page == 1 else (page * results_per_page) - results_per_page
        end_offset = (page * results_per_page)

        after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)

        my_qs = Cotation.objects.filter(market__name="1X2")
        games = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
        game_status=1, 
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .order_by('-league__location__priority','-league__priority')[start_offset:end_offset]


        games_total = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=1),
        game_status=1, 
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .count()

        num_of_pages =  ceil(games_total / results_per_page)
        
        league_games = defaultdict(list)
        location_leagues = get_main_menu()
        
        for game in games:
            league_games[game.league].append(game)
        
        context = {'league_games': league_games, 
            'location_leagues': location_leagues,
            'after_tommorrow': after_tommorrow,
            'range_pages': range(1, num_of_pages + 1),
            'current_page': page
            }


        return self.render_to_response(context)



class AfterTomorrowGames(TemplateResponseMixin, View):

    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):

        page = int(request.GET.get('page')) if request.GET.get('page') else 1

        results_per_page = 80
        start_offset = 0 if page == 1 else (page * results_per_page) - results_per_page
        end_offset = (page * results_per_page)

        after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)

        my_qs = Cotation.objects.filter(market__name="1X2")
        games = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
        game_status=1, 
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .order_by('-league__location__priority','-league__priority')[start_offset:end_offset]


        games_total = Game.objects.filter(start_date__date=tzlocal.now().date() + timezone.timedelta(days=2),
        game_status=1, 
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .count()

        num_of_pages =  ceil(games_total / results_per_page)

        league_games = defaultdict(list)
        location_leagues = get_main_menu()
        
        for game in games:
            league_games[game.league].append(game)
        
        context = {'league_games': league_games, 
            'location_leagues': location_leagues,
            'after_tommorrow': after_tommorrow,
            'range_pages': range(1, num_of_pages + 1),
            'current_page': page
            }
        
        return self.render_to_response(context)



class GameLeague(TemplateResponseMixin, View):

    template_name = 'core/championship_games.html'

    def get(self, request, *args, **kwargs):

        after_tommorrow = tzlocal.now().date() + timezone.timedelta(days=2)

        my_qs = Cotation.objects.filter(market__name='1X2')

        games = Game.objects.filter(start_date__gt=tzlocal.now(),
        game_status=1,
        league__id=self.kwargs["pk"],
        is_visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .prefetch_related(Prefetch('cotations', queryset=my_qs, to_attr='my_cotations'))\
        .order_by('-league__priority')
        
        
        location_leagues = get_main_menu()

        first_game = games.first()
        location_league = str(first_game.league.location.name) + " - " + str(first_game.league.name)
        context = {'games_selected_league': games, 
            'location_leagues': location_leagues,
            'location_league' : location_league,
            'after_tommorrow': after_tommorrow}

        return self.render_to_response(context)


class CotationsView(View):
    
    def get(self, request, *args, **kwargs):

        gameid = self.kwargs['gameid']
        cotations_by_kind = {}

        cotations_of_game = Cotation.objects.filter(game_id=gameid).filter(~Q(market__name='1X2')).filter(Q(market__isnull=False))			
        
        markets = Market.objects.all().prefetch_related(Prefetch('cotations', queryset=cotations_of_game, to_attr='my_cotations')).order_by('name')
                                
        cotations_serialized = {}
        for market in markets:
            if market.my_cotations:		
                cotations_serialized[market.name] = serializers.serialize("json", market.my_cotations, use_natural_foreign_keys=True)

        return UnicodeJsonResponse(cotations_serialized, safe=False)


class BetView(View):

    def post(self, request, *args, **kwargs):

        if int(request.POST['cotation_id']) < 0:
            request.session['ticket'] = {}		
            request.session.modified = True
            return JsonResponse({}, status=204)

        if 'ticket' not in request.session:
            request.session['ticket'] = {}
            request.session['ticket'][request.POST['game_id']] = request.POST['cotation_id']
            request.session.modified = True
            return JsonResponse({}, status=201)
        else:
            if request.session['ticket'].get(request.POST['game_id'], None) == request.POST['cotation_id']:
                del request.session['ticket'][request.POST['game_id']]
                request.session.modified = True
                return JsonResponse({}, status=202)
            else:
                request.session['ticket'][request.POST['game_id']] = request.POST['cotation_id']
                request.session.modified = True
                return JsonResponse({}, status=201)
            

    def get(self, request, *args, **kwargs):
        if 'ticket' not in request.session:
            return HttpResponse("Empty")
        else:
            itens = []

            for key, value in request.session['ticket'].items():
                cotation = Cotation.objects.filter(pk=value).values('pk','game__id','game__name','name', 'price', 'market__name')
                itens.append(cotation.first())

            return JsonResponse( itens , safe=False)
    
    def delete(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        request.session['ticket'].pop(pk)
        request.session.modified = True
        return JsonResponse({}, status=204)


class CreateTicketView(View):

    login_url = reverse_lazy('core:core_home')

    def post(self, request, *args, **kwargs):
        
        from utils.models import GeneralConfigurations, RewardRelated

        try:
            general_config = GeneralConfigurations.objects.get(pk=1)
            max_reward_to_pay = general_config.max_reward_to_pay
            min_number_of_choices_per_bet = general_config.min_number_of_choices_per_bet
            min_bet_value = general_config.min_bet_value
            max_bet_value = general_config.max_bet_value
            min_cotation_sum = general_config.min_cotation_sum
            max_cotation_sum = general_config.max_cotation_sum

        except GeneralConfigurations.DoesNotExist:
            max_bet_value = 1000000
            max_reward_to_pay = 50000
            min_number_of_choices_per_bet = 1
            min_bet_value = 1
            min_cotation_sum = 1
            max_cotation_sum = 100000

        data = {
            'success': True
        }

        ticket_value = request.POST.get('ticket_value', None)
        client_name = request.POST.get('client_name', None)
        cellphone = request.POST.get('telefone', None)

        accepted_conditions = request.POST.get('accepted_conditions', False)
        
        if not request.user.is_authenticated or request.user.has_perm('user.be_seller'):
            if not client_name or len(client_name) < 4:
                data['success'] =  False
                data['message'] =  "Digite o nome do cliente (4 dígitos ou mais)."
                return UnicodeJsonResponse(data)

        if request.user.is_superuser or request.user.has_perm('user.be_manager'):
            data['success'] =  False
            data['message'] =  """Desculpe, Contas administradoras ou Gerentes
            não são apropriados para criarem apostas. <br /> 
            Use contas normais ou conta de cambista."""
            return UnicodeJsonResponse(data)

        if client_name and cellphone:
            if len(client_name) > 40 or len(cellphone) > 14:
                data['success'] =  False
                data['message'] =  "Erro, O nome do cliente precisa ser menor que 40 dígitos e o telefone menor que 14."
                return UnicodeJsonResponse(data)

        if ticket_value == None:
            data['success'] =  False
            data['message'] =  "Valor da aposta inválido."
            return UnicodeJsonResponse(data)

        
        ticket_bet_value = Decimal(ticket_value)
        
        if ticket_bet_value < min_bet_value:
            data['success'] =  False
            data['message'] =  "A aposta mínima é: R$ " + str(min_bet_value)
            return UnicodeJsonResponse(data)

        if ticket_bet_value > max_bet_value:
            data['success'] =  False
            data['message'] =  "A aposta máxima é: R$ " + str(max_bet_value)
            return UnicodeJsonResponse(data)

        if 'ticket' not in request.session:
            data['success'] =  False
            data['message'] =  "Selecione algumas cotações."
            data['clear_cookies'] = True
            return UnicodeJsonResponse(data)

        if ticket_bet_value <= 0:
            data['success'] =  False
            data['message'] =  "Valor da aposta inválido."
            return UnicodeJsonResponse(data)

    
        cotation_sum = 1
        game_cotations = []
        for game_id in request.session['ticket']:
            game_contation = None
            try:
                game_contation = Cotation.objects.get(pk=int(request.session['ticket'][game_id]))
                if game_contation.game.start_date < tzlocal.now():
                    data['success'] =  False
                    data['message'] =  "Desculpe, o jogo:" + game_contation.game.name + " já começou, remova-o"
                    return UnicodeJsonResponse(data)

                game_cotations.append(game_contation)
                cotation_sum *= game_contation.price
            except Cotation.DoesNotExist:
                data['success'] =  False
                data['message'] =  "Erro, uma das cotas enviadas não existe."
                return UnicodeJsonResponse(data)


        if cotation_sum < min_cotation_sum:
            data['success'] =  False
            data['message'] =  "A cotação total deve ser maior que "+ str(min_cotation_sum)
            return UnicodeJsonResponse(data)

        if cotation_sum > max_cotation_sum:
            data['success'] =  False
            data['message'] =  "A cotação total deve ser menor que "+ str(max_cotation_sum)
            return UnicodeJsonResponse(data)

        ticket_reward_value = cotation_sum * ticket_bet_value

        if not accepted_conditions:
            if Decimal(ticket_reward_value) > max_reward_to_pay:
                data['success'] =  False
                data['has_to_accept'] = True
                data['message'] =  "O valor máximo pago pela banca para o valor apostado é: R$" + str(max_reward_to_pay) + ". Seu prêmio será reajustado para esse valor."
                return UnicodeJsonResponse(data)

            for reward_related in RewardRelated.objects.all().order_by('value_max','pk'):
                if ticket_bet_value <= reward_related.value_max:
                    data['success'] =  False
                    data['has_to_accept'] = True
                    data['message'] =  "O valor máximo pago pela banca para o valor de "+ str( round(ticket_bet_value, 2) ) + " R$ é de " + str(reward_related.reward_value_max) + " R$. Seu prêmio será reajustado para esse valor."
                    return UnicodeJsonResponse(data)

        if len(game_cotations) < min_number_of_choices_per_bet:
            data['success'] =  False
            data['message'] =  "Desculpe, Aposte em pelo menos " + str(min_number_of_choices_per_bet) + " jogo."
            return UnicodeJsonResponse(data)

        if data['success']:
            ticket = Ticket(				
                value=ticket_bet_value,
                creation_date = tzlocal.now(),
                payment=Payment.objects.create(payment_date=None), 
                reward=Reward.objects.create(reward_date=None)
            )
            ticket.save()

            if request.user.has_perm('user.be_seller'):
                ticket.seller=request.user.seller
                ticket.normal_user=NormalUser.objects.create(first_name=client_name, cellphone=cellphone)
            else:
                if request.user.is_authenticated:
                    ticket.user=request.user.punter
                else:
                    ticket.normal_user=NormalUser.objects.create(first_name=client_name, cellphone=cellphone)
            
            ticket.reward.save()
            ticket.save()

            for current_cotation in game_cotations:
                ticket.cotations.add(current_cotation)
                CotationHistory(
                    id=current_cotation.pk,
                    original_cotation=current_cotation.pk,
                    ticket=ticket,
                    name=current_cotation.name,
                    start_price=current_cotation.start_price,
                    price=current_cotation.price,
                    game=current_cotation.game,
                    market=current_cotation.market								
                ).save()
        

            data['message'] = """
                Bilhete N° <span class='ticket-number-after-create'> """ +  str(ticket.pk) + """</span>
                <br /> Para acessar detalhes do Ticket, entre no painel do cliente
                <br /> Realize o pagamento com um de nossos colaboradoes usando o número do Ticket
                <br /><br />
                <a href='/ticket/""" + str(ticket.pk) + """' class='waves-effect waves-light btn text-white see-ticket-after-create hoverable'> Ver Ticket </a>
            """
            if request.user.has_perm('user.be_seller'):
                if not ticket.validate_ticket(request.user)['success']:
                    data['not_validated'] =  "<span class='no_credit_message'> Você não tem saldo para validar o Ticket !!! <br /></span>"
                    data['message'] = data['not_validated'] + data['message']

                    request.session['ticket'] = {}
                    request.session.modified = True
                    return UnicodeJsonResponse(data)
                else:
                    request.session['ticket'] = {}
                    request.session.modified = True
                    return UnicodeJsonResponse(data)
            else:
                request.session['ticket'] = {}
                request.session.modified = True
                return UnicodeJsonResponse(data)


class TicketDetail(TemplateResponseMixin, View):


    template_name = 'core/ticket_details.html'

    def get(self, request, *args, **kwargs):
        try:
            ticket = Ticket.objects.get(pk=self.kwargs["pk"])
        except Ticket.DoesNotExist:
            self.template_name = 'core/ticket_not_found.html'
            return self.render_to_response(context={})

        from utils.models import TicketCustomMessage

        cotations_history = CotationHistory.objects.filter(ticket=ticket.pk)
        
        if cotations_history.count() > 0 and ticket.is_visible == True:

            cotations_values = {}
            for current_cotation in cotations_history:
                cotations_values[current_cotation.original_cotation] = current_cotation.price

            content = "<CENTER> -> " + settings.APP_VERBOSE_NAME.upper() + " <- <BR>"
            content += "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
            
            if ticket.seller:
                content += "<CENTER> CAMBISTA: " + ticket.seller.first_name + "<BR>"
            if ticket.normal_user:
                content += "<CENTER> CLIENTE: " + ticket.normal_user.first_name + "<BR>"
            if ticket.user:
                content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

            content += "<CENTER> APOSTA: R$" + str("%.2f" % ticket.value) + "<BR>"
            content += "<CENTER> COTA TOTAL: " + str("%.2f" % ticket.cotation_sum() ) + "<BR>"
            if ticket.reward:
                content += "<CENTER> GANHO POSSIVEL: R$" + str("%.2f" % ticket.reward.real_value) + "<BR>"
            if ticket.payment:
                content +=  "<CENTER> STATUS: " + ticket.payment.status_payment + "<BR>"
            content += "<CENTER> DATA: " + ticket.creation_date.strftime('%d/%m/%Y %H:%M')
            content += "<BR><BR>"
            
            content += "<LEFT> APOSTAS <BR>"
            content += "<LEFT>-------------------------------> <BR>"

            for cotation in ticket.cotations.all():
                content += "<LEFT>" + cotation.game.name + "<BR>"
                content += "<LEFT>" + cotation.game.start_date.strftime('%d/%m/%Y %H:%M') + "<BR>"
                if cotation.market:
                    content += "<LEFT>"+ cotation.market.name + "<BR>"
                content += "<LEFT>" + cotation.name + " --> " + str("%.2f" % cotations_values[cotation.pk]) + "<BR>"

                content += "<RIGHT> Status: " +  cotation.get_settlement_display() + "<BR>"
                
                content += "<CENTER>-------------------------------> <BR>"
            content += "<CENTER> "+ settings.APP_VERBOSE_NAME + "<BR>"

            if TicketCustomMessage.objects.first():            
                phrases = TicketCustomMessage.objects.first().text.replace("\r","").split("\n")

                for phrase in phrases:                
                    content += "<CENTER> " + phrase + "<BR>"

            content += "#Intent;scheme=quickprinter;package=pe.diegoveloper.printerserverapp;end;"			      
            
            context = {'ticket': ticket, 
            'print': content,'cotations_values':cotations_values, 
            'show_ticket': True, 'base_url': request.get_host()}
        else:
            context = {'show_ticket': False}

        return self.render_to_response(context)


class AppDownload(View, TemplateResponseMixin):

    template_name = 'core/app_download.html'

    def get(self, request):
        return self.render_to_response({})


class RulesView(View, TemplateResponseMixin):

    template_name = 'core/rules.html'

    def get(self, request):
        from utils.models import RulesMessage
        rules_text = RulesMessage.objects.first()
        if rules_text:
            return self.render_to_response({'rules': rules_text.text})
        return self.render_to_response({'rules':"Sem regulamento ainda."})
        
