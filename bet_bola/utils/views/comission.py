from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.seller_comission import SellerComissionSerializer
from utils.serializers.manager_comission import ManagerComissionSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import SellerComission, ManagerComission
from filters.mixins import FiltersMixin
from core.cacheMixin import CacheKeyGetMixin

class SellerComissionView(CacheKeyGetMixin, FiltersMixin, ModelViewSet):
    queryset = SellerComission.objects.all()
    serializer_class = SellerComissionSerializer
    cache_group = 'seller_comission_adm'
    caching_time = 60

    
    filter_mappings = {
        'seller': 'seller_related',
        'store':'store'
    }

class ManagerComissionView(CacheKeyGetMixin, FiltersMixin, ModelViewSet):
    queryset = ManagerComission.objects.all()
    serializer_class = ManagerComissionSerializer
    cache_group = 'manager_comission_adm'
    caching_time = 60
    
    filter_mappings = {
        'manager': 'manager_related',
        'store':'store'
    }

