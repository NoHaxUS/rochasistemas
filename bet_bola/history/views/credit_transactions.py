from django.db.models import Q
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from history.paginations import CreditTransactionsPagination
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.models import CreditTransactions
from history.serializers.credit_transactions import CreditTransactionsSerializer
import datetime

class CreditTransactionsView(FiltersMixin, ModelViewSet):
    queryset = CreditTransactions.objects.all()
    serializer_class = CreditTransactionsSerializer
    pagination_class = CreditTransactionsPagination
    permission_classes = [BaseHistoryPermission]

    filter_mappings = {
        'creditor':'creditor__username__icontains',		
        'seller':'user__username__icontains',
        'transferred_amount_above': 'transferred_amount__gt',
        'transferred_amount_under': 'transferred_amount__lt',
        'start_creation_date':'transaction_date__date__gte',
        'end_creation_date':'transaction_date__date__lte',
    }    
    
    filter_value_transformations = {        
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),        
    }


    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return CreditTransactions.objects.filter(user=user)            
        elif user.user_type == 3:
            return CreditTransactions.objects.filter(Q(creditor__pk=user.pk) | Q(user=user))            
        return CreditTransactions.objects.filter(store=user.my_store)
