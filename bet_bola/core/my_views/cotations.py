from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from core.models import CotationCopy
from core.serializers.cotation import CotationCopySerializer, CotationModifiedSerializer, CotationSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore, CanModifyCotation
from core.models import CotationModified, Cotation
from core.paginations import CotationsListSetPagination
from filters.mixins import FiltersMixin


class CotationCopyView(ModelViewSet):
    queryset = CotationCopy.objects.all()
    serializer_class = CotationCopySerializer
    permission_classes = [StoreIsRequired,]


class CotationModifiedView(ModelViewSet):
    queryset = CotationModified.objects.all()
    serializer_class = CotationModifiedSerializer
    permission_classes = [StoreIsRequired, UserIsFromThisStore, CanModifyCotation]

    def perform_create(self, serializer):
        store = serializer.validated_data['store']
        cotation = serializer.validated_data['cotation']
        price = serializer.validated_data['price']
        if CotationModified.objects.filter(store=store, cotation=cotation).exists():
            cotation_modified = CotationModified.objects.get(store=store, cotation=cotation)
            cotation_modified.price = price
            cotation_modified.save()
            return cotation_modified
        super(CotationModifiedView, self).perform_create(serializer)


class CotationView(FiltersMixin, ModelViewSet):
    queryset = Cotation.objects.all()
    serializer_class = CotationSerializer       
    permission_classes = [StoreIsRequired,]
    pagination_class = CotationsListSetPagination

    filter_mappings = {
        'game_name':'game__name__icontains',
        'market_name': 'market__name__icontains',
        'game_name': 'game__name__icontains',
        'cotation_id': 'id'
    }
    