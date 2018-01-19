from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import get_template
from django.views.generic import View
from datetime import datetime
from .utils import updating_games, populating_bd
from io import BytesIO
from core.models import BetTicket,Cotation
from fpdf import FPDF
import urllib

class Update(View):
	def get(self, request, *args, **kwargs):
		updating_games()
		return redirect('core:home')

class PopulatingBD(View):
	def get(self, request, *args, **kwargs):
		populating_bd()
		return redirect('core:home')


class printTicket(View):
	def get(self, request, *args, **kwargs):

		ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])
		date = ticket.creation_date.strftime('%d/%m/%Y %H:%M')

		content = "<CENTER> TICKET: <BIG>" + str(ticket.pk) + "<BR>"
		content += "<CENTER> CLIENTE: " + ticket.user.first_name + "<BR>"

		if ticket.seller != None:
			content += "<CENTER> COLABORADOR: " + ticket.seller.first_name

		content += "<CENTER> DATA: " + date
		content += "<BR><BR>"

		content += "<LEFT> APOSTAS <BR>"
		content += "<CENTER>----------------------------------------------- <BR>"

		for c in ticket.cotations.all():
			content += "<LEFT>" + c.game.name + "<BR>"
			game_date = c.gamestart_game_date.strftime('%d/%m/%Y %H:%M')
			content += "<LEFT>" + game_date + "<BR>"
			content += "<LEFT>"+ c.kind + "<BR>"
			content += "<LEFT>" + c.name + " --> " + str(c.value) + "<BR>"

			if c.game.odds_calculated:
				content += "<RIGHT> Status: Fechado - " + ("Venceu" if c.winning else "Perdeu") + "<BR>"
			else:
				content += "<RIGHT> Status: Em Aberto"				
			
			content += "<CENTER> ----------------------------------------------- <BR>"
			content += "<CENTER> BET BOLA"

		return render(request, "ticket.html", {'content': content})





class PDF(View):
	def get(self, request, *args, **kwargs):
		ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'inline; filename="ticket.pdf"'

		date = 'DATA: ' + ticket.creation_date.strftime('%d/%m/%Y %H:%M')

		pdf = FPDF('P', 'mm', (231, 297 + ticket.cotations.count() * 84))
		pdf.add_page()
		pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)		
		pdf.set_font('DejaVu','',30)		
		#pdf.set_text_color(105,105,105)
		string = 'TICKET:' + str(ticket.pk)
		pdf.text(76,12, string)		
		string = 'CLIENTE: ' + ticket.user.first_name								
		pdf.text(76,24,string)									
		pdf.text(76,36, date)
		if ticket.seller != None:
			string = 'COLABORADOR: ' +  ticket.seller.first_name
			#string = "COLABORADOR PABLO"
			pdf.text(76,48,string)
		pdf.text(4,76,'APOSTAS')		
		pdf.text(0, 82,'--------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
		h = 86
		
		for c in ticket.cotations.all():
			h=h+8
			pdf.text(4,h,c.game.name)
			h=h+14
			pdf.text(4,h, c.game.start_game_date.strftime('%d/%m/%Y %H:%M'))
			h=h+14			
			pdf.text(4,h,c.kind)
			h=h+14
			pdf.text(4,h,c.name)			
			pdf.text(190,h,str(c.value))
			h=h+14
			if c.game.odds_calculated:
				pdf.text(4,h,"Status:")			
				pdf.text(140,h,"Fechado - " + ("Venceu" if c.winning else "Perdeu"))				
			else:
				pdf.text(4,h,"Status:")			
				pdf.text(180,h,"Em Aberto")

			h=h+14
			pdf.text(0,h,'---------------------------------------------------------------------------------------------------------------------------------------------------------')			

		pdf.text(92,h+20,'Bet Bola')
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
				for cotation in Cotation.objects.all():
					new_value = round(cotation.original_value * percentual,2)
					if new_value > 1.25:
						cotation.value = round(cotation.original_value * percentual,2)
						cotation.save()
			else:
				return HttpResponse("Você não tem permissão para isso baby.")

		else:
			return HttpResponse("Não está Logado.")

		return HttpResponse("Percentual Alterado.")


class TestJson(View):
	def get(self, request, *args, **kwargs):
		return JsonResponse({
				    "data": [
				        {
				            "id": 1,
				            "name": "3Way Result",
				            "bookmaker": {
				                "data": [
				                    {
				                        "id": 2,
				                        "name": "bet365",
				                        "odds": {
				                            "data": [
				                                {
				                                    "label": "1",
				                                    "value": "2.29",
				                                    "winning": False,
				                                    "handicap": None,
				                                    "total": None,
				                                    "last_update": {
				                                        "date": "2017-11-28 19:54:03.000000",
				                                        "timezone_type": 3,
				                                        "timezone": "UTC"
				                                    }
				                                },
				                                {
				                                    "label": "X",
				                                    "value": "3.10",
				                                    "winning": True,
				                                    "handicap": None,
				                                    "total": None,
				                                    "last_update": {
				                                        "date": "2017-11-28 19:54:04.000000",
				                                        "timezone_type": 3,
				                                        "timezone": "UTC"
				                                    }
				                                },
				                                {
				                                    "label": "2",
				                                    "value": "3.20",
				                                    "winning": None,
				                                    "handicap": None,
				                                    "total": None,
				                                    "last_update": {
				                                        "date": "2017-11-28 19:54:04.000000",
				                                        "timezone_type": 3,
				                                        "timezone": "UTC"
				                                    }
				                                }
				                            ]
				                        }
				                    }
				                ]
				            }
				        }]})