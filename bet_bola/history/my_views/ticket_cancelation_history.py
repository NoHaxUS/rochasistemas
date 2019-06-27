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
        'start_creation_date':'date__gte',		
        'end_creation_date':'date__lte',
        'paid_by': 'who_paid__pk',
        'cancelled_by': 'who_cancelled__pk',
	}    

    def get_queryset(self):
        return TicketCancelationHistory.objects.filter(store=self.request.user.my_store)