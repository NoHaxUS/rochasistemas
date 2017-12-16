from django.http import HttpResponse
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
