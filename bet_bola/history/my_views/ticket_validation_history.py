from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.paginations import TicketValidationHistoryPagination
from history.models import TicketValidationHistory
from history.serializers.ticket_validation_history import TicketValidationHistorySerializer



class TicketValidationHistoryView(FiltersMixin, ModelViewSet):
    queryset = TicketValidationHistory.objects.all()
    serializer_class = TicketValidationHistorySerializer
    pagination_class = TicketValidationHistoryPagination
    permission_classes = [BaseHistoryPermission,]
    
    filter_mappings = {
        'start_creation_date':'date__gte',		
        'end_creation_date':'date__lte',
        'paid_by': 'who_validated__pk',        
	}    

    def get_queryset(self):
        return TicketValidationHistory.objects.filter(store=self.request.user.my_store)
