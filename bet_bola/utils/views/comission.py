from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.seller_comission import SellerComissionSerializer
from utils.serializers.manager_comission import ManagerComissionSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import SellerComission, ManagerComission
from filters.mixins import FiltersMixin

class SellerComissionView(FiltersMixin, ModelViewSet):
    queryset = SellerComission.objects.all()
    serializer_class = SellerComissionSerializer

    
    filter_mappings = {
        'seller': 'seller_related',
        'store':'store'
    }

class ManagerComissionView(FiltersMixin, ModelViewSet):
    queryset = ManagerComission.objects.all()
    serializer_class = ManagerComissionSerializer
    
    filter_mappings = {
        'manager': 'manager_related',
        'store':'store'
    }

