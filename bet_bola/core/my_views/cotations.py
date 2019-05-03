from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from core.models import CotationCopy
from core.serializers.cotation import CotationCopySerializer, CotationModifiedSerializer, CotationSerializer
from core.permissions import StoreIsRequired, CotationModifyPermission
from core.models import CotationModified, Cotation

class CotationCopyView(ModelViewSet):
    queryset = CotationCopy.objects.all()
    serializer_class = CotationCopySerializer
    permission_classes = [StoreIsRequired,]


class CotationModifiedView(ModelViewSet):
    queryset = CotationModified.objects.all()
    serializer_class = CotationModifiedSerializer
    permission_classes = [CotationModifyPermission,]


class CotationView(ModelViewSet):
    queryset = Cotation.objects.all()
    serializer_class = CotationSerializer       
    permission_classes = [StoreIsRequired,]

    def list(self, request, pk=None):
        queryset = Cotation.objects.all()        

        if request.GET.get('game_id'):            
            queryset = queryset.filter(game__id=request.GET.get('game_id'))

        if request.GET.get('market_excluded'):
            queryset = queryset.exclude(market__name=request.GET.get('market_excluded'))

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)

