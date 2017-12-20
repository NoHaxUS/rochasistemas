from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.template.loader import get_template
from django.views.generic import View
from datetime import datetime
from .utils import updating_games, populating_bd
from fpdf import FPDF
from io import BytesIO


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
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'inline; filename="somefilename.pdf"'

		#pdf = FPDF()
		pdf = FPDF('P', 'mm', (100, 150))
		pdf.add_page()
		pdf.set_font('Arial', 'B', 16)
		pdf.cell(40, 10, 'Fabiano CôCô')
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