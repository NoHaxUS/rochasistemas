from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.template.loader import get_template
from django.views.generic import View
from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from .utils import updating_games, populating_bd

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


class GeneratePdf(View):
	def get(self, request, *args, **kwargs):
		data = {
			'today': datetime.now(), 
			'amount': 39.99,
			'customer_name': 'Cooper Mann',
			'order_id': 1233434,
		}
		pdf = render_to_pdf('utils/ticket.html', data)
		return HttpResponse(pdf, content_type='application/pdf')

class Update(View):
	def get(self, request, *args, **kwargs):
		updating_games()
		return redirect('core:home')

class PopulatingBD(View):
	def get(self, request, *args, **kwargs):
		populating_bd()
		return redirect('core:home')	