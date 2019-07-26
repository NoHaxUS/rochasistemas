from rest_framework.viewsets import ModelViewSet
from filters.mixins import FiltersMixin
from history.paginations import SellerCashierPagination
from history.models import SellerCashierHistory
from history.permissions import BaseHistoryPermission
from history.serializers.seller_cashier import SellerCashierSerializer

class SellerCashierView(FiltersMixin, ModelViewSet):
    queryset = SellerCashierHistory.objects.all()
    serializer_class = SellerCashierSerializer
    pagination_class = SellerCashierPagination
    permission_classes = [BaseHistoryPermission]  

    filter_mappings = {
		'register_by':'register_by__pk',
        'entries_above':'entry__gt',
        'entries_under':'entry__lt',
        'start_creation_date':'date__gte',
        'end_creation_date':'date__lte',
    }

    def get_queryset(self):
        user = self.request.user        
        if user.user_type == 2:
            return SellerCashierView.objects.filter(seller__pk=self.request.user.pk)
        elif user.user_type == 3:
            return SellerCashierView.objects.filter(seller__my_manager__pk=self.request.user.pk).order_by('-date')
        return SellerCashierView.objects.filter(store=user.my_store).order_by('-date')
