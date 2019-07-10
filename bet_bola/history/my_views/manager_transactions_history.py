from django.db.models import Q
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from history.paginations import ManagerTransactionsHistoryPagination
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.models import ManagerTransactions
from history.serializers.manager_transactions_history import ManagerTransactionsSerializer


class ManagerTransactionsHistoryView(FiltersMixin, ModelViewSet):
    queryset = ManagerTransactions.objects.all()
    serializer_class = ManagerTransactionsSerializer
    pagination_class = ManagerTransactionsHistoryPagination
    permission_classes = [BaseHistoryPermission]

    filter_mappings = {
        'creditor':'creditor__pk',		
        'seller':'user__pk',
        'transferred_amount_above': 'transferred_amount__gt',
        'transferred_amount_under': 'transferred_amount__lt',
        'start_creation_date':'transaction_date__gte',
        'end_creation_date':'transaction_date__lte',
	}    

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return ManagerTransactions.objects.filter(user=user)            
        elif user.user_type == 3:
            return ManagerTransactions.objects.filter(Q(creditor__pk=user.pk) | Q(user=user))            
        return ManagerTransactions.objects.filter(store=user.my_store)
