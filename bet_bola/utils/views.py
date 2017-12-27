from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.template.loader import get_template
from django.views.generic import View
from datetime import datetime
from .utils import updating_games, populating_bd
from fpdf import FPDF
from io import BytesIO
from core.models import BetTicket

class Update(View):
	def get(self, request, *args, **kwargs):
		updating_games()
		return redirect('core:home')

class PopulatingBD(View):
	def get(self, request, *args, **kwargs):
		populating_bd()
		return redirect('core:home')

class PDF(View):
	def get(self, request, *args, **kwargs):
		ticket = get_object_or_404(BetTicket, pk=self.kwargs["pk"])
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'inline; filename="ticket.pdf"'

		date = 'data: ' + str(ticket.creation_date.date().day) + "/" + str(ticket.creation_date.date().month) + "/" + str(ticket.creation_date.date().year)

		pdf = FPDF('P', 'mm', (231, 297 + ticket.cotations.count() * 84))
		pdf.add_page()
		pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)		
		pdf.set_font('DejaVu','',30)				
		pdf.set_text_color(105,105,105)
		string = 'TICKET #id: ' + str(ticket.pk)
		pdf.text(76,12, string)		
		string = 'CLIENTE: ' + ticket.user.first_name.upper()										
		pdf.text(76,26,string)		
		string = 'COLABORADOR: ' + (' ' if ticket.seller == None else ticket.seller.first_name)
		pdf.text(76,40,string)										
		pdf.text(76,54, date)			
		pdf.text(4,74,'APOSTA')
		pdf.text(185,74,'COTAS')			
		pdf.text(0, 82,'--------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
		h = 86
		
		for c in ticket.cotations.all():
			h=h+8
			pdf.text(4,h,c.kind)
			h=h+14
			pdf.text(4,h,c.game.name)
			h=h+14
			pdf.text(4,h, str(c.game.start_game_date.date().day) +"/"+str(c.game.start_game_date.date().month)+"/"+str(c.game.start_game_date.date().day)+ " " +str(c.game.start_game_date.hour)+":"+str(c.game.start_game_date.minute))
			h=h+14			
			pdf.text(4,h,c.kind)
			h=h+14
			pdf.text(4,h,c.name)			
			pdf.text(190,h,str(c.value))
			h=h+14
			if c.game.odds_calculated:
				pdf.text(4,h,"Status:")			
				pdf.text(190,h,"Em Aberto")
			else:
				pdf.text(4,h,"Status:")			
				pdf.text(140,h,"Fechado - " + ("Venceu" if c.winning else "Perdeu"))

			h=h+14
			pdf.text(0,h,'---------------------------------------------------------------------------------------------------------------------------------------------------------')			

		pdf.text(92,h+20,'Bet Bola')
		buffer = pdf.output(dest='S').encode('latin-1')

		response.write(buffer)
		return response


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