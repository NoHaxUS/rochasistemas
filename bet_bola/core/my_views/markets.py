from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Prefetch, Count, Q
from filters.mixins import FiltersMixin
from core.paginations import StandardSetPagination
from core.models import Market, Cotation, Store
from core.serializers.market import MarketCotationSerializer, MarketSerializer
from core.permissions import StoreIsRequired


class MarketView(FiltersMixin, ModelViewSet):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer    
    permission_classes = [StoreIsRequired]
    pagination_class = StandardSetPagination

    filter_mappings = {
        'market_name':'name__icontains',        
    }
    


class MarketCotationView(ModelViewSet):
    queryset = Market.objects.exclude(cotations__market__name='1X2').distinct()
    serializer_class = MarketCotationSerializer    
    permission_classes = [StoreIsRequired]
    
    def list(self, request, pk=None):
        queryset = Market.objects.all()

        game_id = request.GET.get('game_id', None)
        if not game_id:
            return Response({
                'success': False,
                'message': 'A ID do jogo é obrigatória'
            })

        my_cotations_qs = Cotation.objects.filter(game=game_id).exclude(market__name='1X2')
        queryset = queryset.prefetch_related(Prefetch('cotations', queryset=my_cotations_qs, to_attr='my_cotations'))
        queryset = queryset.annotate(cotations_count=Count('cotations', filter=Q(cotations__game__pk=game_id))).filter(cotations_count__gt=0).exclude(name='1X2')


        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
              
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)
        