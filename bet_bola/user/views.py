from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import permissions, mixins, generics, status
from rest_framework.response import Response
from user.models import Punter, NormalUser, CustomUser, Seller, Manager, Admin
from ticket.models import Ticket
from .serializers import PunterSerializer, NormalUserSerializer, SellerSerializer, ManagerSerializer, AdminSerializer
from .permissions import IsSuperUser, PunterViewPermission, SellerViewPermission, ManagerViewPermission, StoreGiven

