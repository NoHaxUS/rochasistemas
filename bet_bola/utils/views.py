from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import get_template
from django.views.generic import View
from django.utils import timezone
from django.core import serializers
from core.models import Ticket,Cotation,CotationHistory, Reward
from user.models import Seller
from .models import TicketCustomMessage
from django.conf import settings
from fpdf import FPDF
from django.db.models import F, Q, When, Case
import urllib
import json
from utils.response import UnicodeJsonResponse
from  collections import defaultdict
from django.core import serializers
import utils.timezone as tzlocal
from core.models import Game, League
from django.db.models import Count


class ValidateTicket(View):

    def post(self, request, *args, **kwargs):
        ticket_id = request.POST['ticket_id']

        ticket = Ticket.objects.filter(pk=ticket_id)

        if ticket.count() > 0:
            return UnicodeJsonResponse(ticket.first().validate_ticket(request.user.seller))
        else:
            return UnicodeJsonResponse({
                'sucess':False,
                'message': 'Esse bilhete não existe.'
            })


class CancelTicket(View):

    def post(self, request, *args, **kwargs):
        ticket_id = request.POST['ticket_id']

        ticket = Ticket.objects.filter(pk=ticket_id)

        if ticket.count() > 0:
            return UnicodeJsonResponse(ticket.first().cancel_ticket(request.user.seller))
        else:
            return UnicodeJsonResponse({
                'sucess':False,
                'message': 'Esse bilhete não existe.'
            })


class PayTicketWinners(View):

    def post(self, request, *args, **kwargs):
        tickets = Ticket.objects.filter(payment__who_set_payment=request.user.seller, 
        payment__status_payment='Pago')\
        .exclude(reward__reward_status=Reward.REWARD_STATUS[1][1])
        ticket_winner = [ticket for ticket in tickets if ticket.ticket_status == 'Venceu']
        for ticket in ticket_winner:
            ticket.pay_winner_punter(request.user.seller)
        
        return UnicodeJsonResponse({
            'sucess':True,
            'message': 'Ganhadores Pagos.'
        })


class GetMainMenuView(View):

    def get(self, request, *args, **kwargs):

        games = Game.objects.filter(start_date__gt=tzlocal.now(),
        league__isnull=False,
        game_status=1,
        visible=True)\
        .annotate(cotations_count=Count('cotations')).filter(cotations_count__gte=1)\
        .exclude(Q(league__visible=False) | Q(league__location__visible=False) )\
        .order_by('-league__location__priority', '-league__priority')\
        .values('league__location','league__location__name', 'league')\
        .distinct()

        #print(games)
        item = {}
        for value in games:
            print(value)
            value["league__name"] = League.objects.filter(id=value['league']).values('name').first()['name']
            item[value['league__location__name']]

        return UnicodeJsonResponse(itens, safe=False)
        #location_leagues = defaultdict(set)
        #location_leagues = {}
        
        #for game in games:
        #    if game.league.location:
        #        location_leagues[game.league.location.name].add(serializers.serialize("json", game.league))
        
        #print(leagues)
        #print(serializers.serialize("json", leagues, use_natural_foreign_keys=True))
        #return UnicodeJsonResponse({})

        #return UnicodeJsonResponse(serializers.serialize("json", location_leagues, use_natural_foreign_keys=True), safe=False)


class PDF(View):


    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=self.kwargs["pk"])
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="ticket.pdf"'


        cotations_history = CotationHistory.objects.filter(ticket=ticket.pk)

        cotations_values = {}
        for i_cotation in cotations_history:
            cotations_values[i_cotation.original_cotation] = i_cotation.price


        pdf = FPDF('P', 'mm', (231, 297 + ticket.cotations.count() * 84))
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)		
        pdf.set_font('DejaVu','',30)

        pdf.text(60,15, "-> "+ settings.APP_VERBOSE_NAME.upper() +" <-")
        pdf.text(55,30, 'BILHETE:' + str(ticket.pk))

        if ticket.seller:
            pdf.text(55,96, 'CAMBISTA: ' + ticket.seller.first_name)
        if ticket.normal_user:
            pdf.text(55,40, 'CLIENTE:' + ticket.normal_user.first_name)
        if ticket.user:
            pdf.text(55,40, 'CLIENTE:' + ticket.user.first_name)
								
        pdf.text(55,50, 'DATA: ' + ticket.creation_date.strftime('%d/%m/%Y %H:%M'))
        pdf.text(55,60, "APOSTA: R$" + str("%.2f" % ticket.value) )
        pdf.text(55,72, "COTA TOTAL: " + str("%.2f" % ticket.cotation_sum() ))
        if ticket.reward:
            pdf.text(55,84, "GANHO POSSÍVEL: R$" + str("%.2f" % ticket.reward.real_value) )
        if ticket.payment:
            payment_text = ticket.payment.status_payment
            if len(payment_text) <= 5:
                pdf.text(55,107, "STATUS: " + payment_text )
            else:
                pdf.text(10,107, "STATUS: " + payment_text )
        
        pdf.text(4,130,'APOSTAS')		
        pdf.text(0, 135,'--------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        h = 140
        
        for c in ticket.cotations.all():
            h=h+8
            pdf.text(4,h,c.game.name)
            h=h+14
            pdf.text(4,h, c.game.start_date.strftime('%d/%m/%Y %H:%M'))
            if c.market:
                h=h+14
                pdf.text(4,h, c.market.name)
            h=h+14
            base_line = c.base_line if c.base_line else ''
            pdf.text(4,h,"Cota:" + c.name + ' ' + base_line)			
            pdf.text(190,h,str("%.2f" % cotations_values[c.pk]))
            h=h+14

            pdf.text(4,h,"Status:")			
            pdf.text(170,h, c.get_settlement_display() )				


            h=h+14
            pdf.text(0,h,'---------------------------------------------------------------------------------------------------------------------------------------------------------')			

        pdf.text(80,h+20, settings.APP_VERBOSE_NAME)
        h+=36
        if TicketCustomMessage.objects.first():
            
            phrases = TicketCustomMessage.objects.first().text.replace("\r","").split("\n")            

            for phrase in phrases:                                
                v = 20
                pdf.text(v,h, phrase)
                h+=10

        buffer = pdf.output(dest='S').encode('latin-1')
        response.write(buffer)
        return response

