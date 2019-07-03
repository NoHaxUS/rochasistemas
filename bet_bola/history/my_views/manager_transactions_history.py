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
        'seller':'seller__pk',
        'transferred_amount_above': 'transferred_amount__gt',
        'transferred_amount_under': 'transferred_amount__lt',
        'start_creation_date':'transaction_date__gte',
        'end_creation_date':'transaction_date__lte',
	}    

    def get_queryset(self):
        if self.request.user.has_perm('user.be_manager'):
            return ManagerTransactions.objects.filter(creditor__pk=self.request.user.pk)
        return ManagerTransactions.objects.filter(store=self.request.user.my_store)
