from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from user.permissions import IsAdmin
from core.models import CotationCopy
from core.serializers.cotation import CotationCopySerializer, CotationModifiedSerializer, CotationSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore, CanModifyCotation
from core.models import CotationModified, Cotation
from core.paginations import CotationsListSetPagination
from filters.mixins import FiltersMixin
from core.cacheMixin import CacheKeyDispatchMixin
from utils.cache import invalidate_cache_group
import json
import decimal

class CotationView(FiltersMixin, ModelViewSet):
    queryset = Cotation.objects.all()
    serializer_class = CotationSerializer       
    permission_classes = []
    pagination_class = CotationsListSetPagination    


    @action(methods=['delete'], detail=True, permission_classes=[IsAdmin])
    def reset_cotation_price(self, request, pk=None):
        cotation = self.get_object()                
        CotationModified.objects.filter(cotation=cotation, store=request.user.my_store).delete() 
                
        invalidate_cache_group(
            [
                '/today_games/', 
                '/tomorrow_games/',
                '/after_tomorrow_games/',
                '/search_games/',
                '/market_cotations/'
            ],
                request.user.my_store.pk
            )

        return Response({
                'success': True,
                'message': 'Cota restaurada com Sucesso :)'
            })

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
        if not data:
            data = "{}"       
        data = json.loads(data)        
        cotation_modified = {}                
        for id in data.get('ids'):   
            if data.get('price'):
                cotation_modified['price'] = decimal.Decimal(data.get('price'))
            if data.get('available') is not None:                
                cotation_modified['available'] = data.get('available')

            cotation_modified['cotation'] = id                                   
            serializer = self.get_serializer(data=cotation_modified)               
            serializer.is_valid(raise_exception=True)        
            self.perform_create(serializer)                
        headers = self.get_success_headers(serializer.data)  

        invalidate_cache_group(
            [
            '/today_games/',
            '/tomorrow_games/',
            '/after_tomorrow_games/'
            ], 
            request.user.my_store.pk
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):        
        cotation = serializer.validated_data['cotation']        
        store = self.request.user.my_store
        if CotationModified.objects.filter(store=store, cotation=cotation).exists():            
            cotation_modified = CotationModified.objects.get(store=store, cotation=cotation)                                    
        else:
             cotation_modified = CotationModified(store=store,cotation=cotation)                        
                
        if serializer.validated_data.get('price'):
            cotation_modified.price = serializer.validated_data.get('price')
        if serializer.validated_data.get('available') is not None:            
            cotation_modified.available = serializer.validated_data.get('available')                
        
        cotation_modified.save()
        return cotation_modified
        