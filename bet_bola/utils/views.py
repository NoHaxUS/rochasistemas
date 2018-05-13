from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import get_template
from django.views.generic import View
from django.utils import timezone
from django.core import serializers
from core.models import BetTicket,Cotation,CotationHistory
from user.models import Seller
from django.conf import settings
from fpdf import FPDF
from django.db.models import F, Q, When, Case
import urllib
import json


class PDF(View):

    def get_verbose_cotation(self, cotation_name):
        names_mapping = {'1':'Casa','X':'Empate','x':'Empate','2':'Visitante'}
        return names_mapping.get(cotation_name, cotation_name)


    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="ticket.pdf"'


        cotations_history = CotationHistory.objects.filter(bet_ticket=ticket.pk)

        cotations_values = {}
        for i_cotation in cotations_history:
            cotations_values[i_cotation.original_cotation] = i_cotation.value


        date = 'DATA: ' + ticket.creation_date.strftime('%d/%m/%Y %H:%M')

        pdf = FPDF('P', 'mm', (231, 297 + ticket.cotations.count() * 84))
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)		
        pdf.set_font('DejaVu','',30)
        string = 'TICKET:' + str(ticket.pk)
        pdf.text(65,12, string)
        if ticket.random_user:
            string = 'CLIENTE: ' + ticket.random_user.first_name
        else:
            string = 'CLIENTE: ' + ticket.user.first_name							
        pdf.text(65,24,string)									
        pdf.text(65,36, date)
        pdf.text(65,48, "APOSTA: R$" + str(ticket.value) )
        pdf.text(65,60, "GANHO POSSÍVEL: R$" + str(ticket.reward.value) )
        pdf.text(4,100,'APOSTAS')		
        pdf.text(0, 105,'--------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        h = 110
        
        for c in ticket.cotations.all():
            h=h+8
            pdf.text(4,h,c.game.name)
            h=h+14
            pdf.text(4,h, c.game.start_game_date.strftime('%d/%m/%Y %H:%M'))
            h=h+14			
            pdf.text(4,h,c.kind.name)
            h=h+14
            pdf.text(4,h,"Cota:" + self.get_verbose_cotation(c.name))			
            pdf.text(190,h,str("%.2f" % cotations_values[c.pk]))
            h=h+14
            if not c.winning == None:
                pdf.text(4,h,"Status:")			
                pdf.text(170,h, ("Acertou" if c.winning else "Não acertou"))				
            else:
                pdf.text(4,h,"Status:")			
                pdf.text(180,h,"Em Aberto")

            h=h+14
            pdf.text(0,h,'---------------------------------------------------------------------------------------------------------------------------------------------------------')			

        pdf.text(70,h+20, settings.APP_VERBOSE_NAME)
        pdf.text(20,h+36, "Prazo para Resgate do Prêmio: 48 horas.")
        buffer = pdf.output(dest='S').encode('latin-1')
        response.write(buffer)
        return response


class PercentualReductionCotation(View):
    def get(self, request, *args, **kwargs):
        percentual = float(self.kwargs["percentual"])
        if percentual <= 0 or percentual > 1:
            return HttpResponse("Valor inválido.")

        if  request.user.is_authenticated:
            if request.user.is_superuser:
                Cotation.objects.update(value=F('original_value') * percentual)
                Cotation.objects.update(value=Case(When(value__lt=1,then=1.01),default=F('value')))
                return HttpResponse("Percentual Alterado.")
            else:
                return HttpResponse("Você não tem permissão para isso baby.")

        else:
            return HttpResponse("Não está Logado.")


class GetSellers(View):
    def get(self, request, *args, **kwargs):
        sellers = []
        for seller in Seller.objects.all():
            sellers.append({'login': seller.username + " - Nome: " + seller.first_name})
        data = json.dumps(sellers)
        return HttpResponse(data, content_type='application/json' )

