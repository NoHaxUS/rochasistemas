from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.paginations import TicketValidationPagination
from history.models import TicketValidationHistory
from history.serializers.ticket_validation import TicketValidationSerializer
import datetime


class TicketValidationView(FiltersMixin, ModelViewSet):
    queryset = TicketValidationHistory.objects.all()
    serializer_class = TicketValidationSerializer
    pagination_class = TicketValidationPagination
    permission_classes = [BaseHistoryPermission,]

    filter_mappings = {
        'ticket_id': 'ticket__ticket_id__icontains',
        'start_creation_date':'date__date__gte',		
        'end_creation_date':'date__date__lte',
        'paid_by': 'who_validated__username__icontains',        
	}    

    filter_value_transformations = {        
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),        
    }

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return TicketValidationHistory.objects.filter(who_validated=user,store=self.request.user.my_store).order_by('-date')
        if user.user_type == 3:
            return TicketValidationHistory.objects.filter(Q(who_validated=user)|Q(who_validated__seller__my_manager__pk=user.pk),store=self.request.user.my_store).order_by('-date')
        return TicketValidationHistory.objects.filter(store=user.my_store).order_by('-date')