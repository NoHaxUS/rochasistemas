from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse
from filters.mixins import FiltersMixin
from history.permissions import BaseHistoryPermission
from history.models import ManagerTransactions
from history.serializers.manager_transactions_history import ManagerTransactionsSerializer


class ManagerTransactionsHistoryView(FiltersMixin, ModelViewSet):
    queryset = ManagerTransactions.objects.all()
    serializer_class = ManagerTransactionsSerializer
    permission_classes = [BaseHistoryPermission]

    filter_mappings = {
        'manager':'manager__username__pk',		
        'seller':'seller__username__pk',
        'paid_by': 'who_paid__pk',
        'date': 'transaction_date__date',
	}    

    def get_queryset(self):
        if self.request.user.has_perm('user.be_manager'):
            return ManagerTransactions.objects.filter(manager__pk=self.request.user.pk)
        return ManagerTransactions.objects.filter(store=self.request.user.my_store)
