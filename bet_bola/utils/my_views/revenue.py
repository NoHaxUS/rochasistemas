from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from filters.mixins import FiltersMixin
from ticket.models import Ticket, Reward, Payment
from ticket.serializers.ticket import TicketSerializer, CreateTicketAnonymousUserSerializer, CreateTicketLoggedUserSerializer
from ticket.paginations import TicketPagination
from ticket.permissions import CanCreateTicket, CanPayWinner, CanValidateTicket, CanCancelTicket, CanManipulateTicket
from user.permissions import IsSuperUser
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.models import TicketOwner
from core.models import CotationCopy, Cotation, Store
from utils.models import RewardRestriction
from utils import timezone as tzlocal
from config import settings

class RevenueView(FiltersMixin, ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (
        StoreIsRequired, 
        IsSuperUser|CanManipulateTicket, 
        IsSuperUser|CanCreateTicket
    )
    pagination_class = TicketPagination

    filter_mappings = {
        'ticket_id':'pk',
        'store':'store',
        'ticket_status':'status',
        'created_by': 'creator__username__icontains',
        'paid_by': 'payment__who_paid__username__icontains',
        'start_creation_date':'creation_date__gte',
        'end_creation_date':'creation_date__lte',
        'payment_status':'payment__status',
        'start_payment_date': 'payment__date__gte',
        'end_payment_date': 'payment__date__lte',
        'available': 'available',
    }

    def list(self, request, pk=None):
        from core.models import Store
        store_id = request.GET.get('store')
        store = Store.objects.get(pk=store_id)
        tickets = Ticket.objects.filter(payment__status=2,store=store).exclude(status__in=[0,5,6])
        
        serializer = self.get_serializer(tickets, many=True)

        return Response(serializer.data)