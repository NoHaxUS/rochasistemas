from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.template.loader import get_template
from django.views.generic import View
from datetime import datetime
from .utils import updating_games, populating_bd


class Update(View):
	def get(self, request, *args, **kwargs):
		updating_games()
		return redirect('core:home')

class PopulatingBD(View):
	def get(self, request, *args, **kwargs):
		populating_bd()
		return redirect('core:home')	