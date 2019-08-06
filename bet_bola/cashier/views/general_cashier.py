from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from cashier.serializers.cashier import CashierSerializer, SellersCashierSerializer, ManagersCashierSerializer
from history.paginations import SellerCashierPagination, ManagerCashierPagination, SellersCashierPagination, ManagersCashierPagination
from ticket.paginations import TicketPagination
from ticket.serializers.ticket import TicketSerializer, CreateTicketSerializer
from user.models import Seller, Manager
from utils.models import Entry
from utils import timezone as tzlocal
from config import settings
import json, datetime, decimal


class GeneralCashier(APIView):

    def get(self, request):
        if request.user.is_authenticated:
            entries = 0
            out = 0
            total_release = 0
            comissions = 0
            total_out = 0
            user = request.user 

            if request.user.user_type == 2:
                managers = Manager.objects.none()
                sellers = Seller.objects.filter(pk=user.pk,payment__status=2, my_store=request.user.my_store).distinct()
                for release in Entry.objects.filter(user=user):
                    total_release += release.value                

            elif request.user.user_type == 3:
                managers = Manager.objects.filter(pk=user.pk,manager_assoc__payment__status=2, my_store=request.user.my_store).distinct()
                sellers = Seller.objects.filter(my_manager__pk=user.pk,payment__status=2, my_store=request.user.my_store).distinct()                
                for release in Entry.objects.filter(Q(user=user) | Q(user__in=user.manager.manager_assoc.all())):
                    total_release += release.value

            else:
                managers = Manager.objects.filter(manager_assoc__payment__status=2, my_store=request.user.my_store).distinct()
                sellers = Seller.objects.filter(payment__status=2, my_store=request.user.my_store).distinct()
                for release in Entry.objects.filter(store=request.user.my_store):
                    total_release += release.value     

            for manager in ManagersCashierSerializer(managers, many=True, context={'request':self.request}).data:                        
                comissions += manager['comission']            
                total_out += manager['comission']

            for seller in SellersCashierSerializer(sellers, many=True, context={'request':self.request}).data:            
                entries += seller['entry']
                out += seller['out'] + seller['won_bonus']
                comissions += seller['comission']
                total_out += seller['total_out']

            profit = entries - total_out                                   
                
            data = {
                'entries': entries,
                'out': out,
                'total_release': total_release,
                'comissions': comissions,
                'total_out': total_out,
                'profit': profit
            }    

            return Response(data)
        return Response({})