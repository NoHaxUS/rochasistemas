from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.paginations import TicketCancelationPagination
from history.models import TicketCancelationHistory
from history.serializers.ticket_cancelation import TicketCancelationSerializer
import datetime
from core.cacheMixin import CacheKeyGetMixin


class TicketCancelationView(CacheKeyGetMixin, FiltersMixin, ModelViewSet):
    queryset = TicketCancelationHistory.objects.all()
    serializer_class = TicketCancelationSerializer
    pagination_class = TicketCancelationPagination
    permission_classes = [BaseHistoryPermission]
    cache_group = 'ticket_cancelation_view_adm'
    caching_time = 60

    
    filter_mappings = {
        'ticket_id': 'ticket__ticket_id__contains',
        'start_creation_date':'date__date__gte',		
        'end_creation_date':'date__date__lte',
        'paid_by': 'who_paid__username__icontains',
        'cancelled_by': 'who_cancelled__username__icontains',
	}    

    filter_value_transformations = {        
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),        
    }

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return TicketCancelationHistory.objects.filter(who_cancelled=user,store=self.request.user.my_store).order_by('-date')
        if user.user_type == 3:
            return TicketCancelationHistory.objects.filter(Q(who_cancelled=user)|Q(who_cancelled__seller__my_manager__pk=user.pk),store=self.request.user.my_store).order_by('-date')
        return TicketCancelationHistory.objects.filter(store=user.my_store).order_by('-date')