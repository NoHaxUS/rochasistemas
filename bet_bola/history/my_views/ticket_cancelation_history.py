from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.paginations import CancelationHistoryPagination
from history.models import TicketCancelationHistory
from history.serializers.ticket_cancelation_history import TicketCancelationHistorySerializer

class TicketCancelationHistoryView(FiltersMixin, ModelViewSet):
    queryset = TicketCancelationHistory.objects.all()
    serializer_class = TicketCancelationHistorySerializer
    pagination_class = CancelationHistoryPagination
    permission_classes = [BaseHistoryPermission]
    
    filter_mappings = {
        'ticket_id': 'ticket__ticket_id__contains',
        'start_creation_date':'date__gte',		
        'end_creation_date':'date__lte',
        'paid_by': 'who_paid__pk',
        'cancelled_by': 'who_cancelled__pk',
	}    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return TicketCancelationHistory.objects.filter(who_cancelled=user,store=self.request.user.my_store).order_by('-date')
        if user.user_type == 3:
            return TicketCancelationHistory.objects.filter(Q(who_cancelled=user)|Q(who_cancelled__seller__my_manager__pk=user.pk),store=self.request.user.my_store).order_by('-date')
        return TicketCancelationHistory.objects.filter(store=user.my_store).order_by('-date')