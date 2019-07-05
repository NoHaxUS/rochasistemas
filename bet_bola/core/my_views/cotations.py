from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from core.models import CotationCopy
from core.serializers.cotation import CotationCopySerializer, CotationModifiedSerializer, CotationSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore, CanModifyCotation
from core.models import CotationModified, Cotation
from core.paginations import CotationsListSetPagination
from filters.mixins import FiltersMixin
import json

class CotationView(FiltersMixin, ModelViewSet):
    queryset = Cotation.objects.all()
    serializer_class = CotationSerializer       
    permission_classes = [StoreIsRequired,]
    pagination_class = CotationsListSetPagination

    filter_mappings = {
        'game_id':'game__pk',
        'market_name': 'market__name__icontains',
        'game_name': 'game__name__icontains',
        'cotation_id': 'pk'
    }

class CotationCopyView(ModelViewSet):
    queryset = CotationCopy.objects.all()
    serializer_class = CotationCopySerializer
    permission_classes = [StoreIsRequired,]


class CotationModifiedView(ModelViewSet):
    queryset = CotationModified.objects.all()
    serializer_class = CotationModifiedSerializer
    permission_classes = [CanModifyCotation]

    def create(self, request, *args, **kwargs):
        data = request.data.get('data')        
        data = json.loads(data)        
        serializer = self.get_serializer(data=data)               
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)                
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):        
        cotation = serializer.validated_data['cotation']
        price = serializer.validated_data['price']
        store = self.request.user.my_store
        if CotationModified.objects.filter(store=store, cotation=cotation).exists():
            cotation_modified = CotationModified.objects.get(store=store, cotation=cotation)
            cotation_modified.price = price
            cotation_modified.save()
            return cotation_modified
        return CotationModified.objects.create(store=store,cotation=cotation,price=price)


    