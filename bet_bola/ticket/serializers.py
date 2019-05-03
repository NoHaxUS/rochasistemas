from rest_framework import serializers, status
from core.serializers import CotationSerializer,CotationTicketSerializer
from user.models import Seller, Manager,CustomUser
from core.models import Store, Cotation
from user.serializers import NormalUserSerializer, PunterSerializer, SellerSerializer
from utils.utils import general_configurations
from utils import timezone as tzlocal
from .models import *


