from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import Count
from .models import Store, CotationHistory, CotationModified, Sport, Game, League, Location, Market, Cotation
from ticket.models import Ticket
from user.models import CustomUser
import utils.timezone as tzlocal
from django.utils import timezone
from utils.models import GeneralConfigurations

