from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Prefetch, Count, Q, F
from filters.mixins import FiltersMixin
from core.paginations import StandardSetPagination
from core.models import Market, Cotation, Store, CotationModified
from core.serializers.market import MarketCotationSerializer, MarketSerializer
from core.permissions import StoreIsRequired
from utils.models import MarketRemotion, MarketModified
from core.cacheMixin import CacheKeyDispatchMixin


class MarketView(FiltersMixin, ModelViewSet):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer    
    permission_classes = []
    pagination_class = StandardSetPagination
    
    filter_mappings = {
        'market_name':'name__icontains',        
    }       
    
    def get_queryset(self):                                
        available = self.request.GET.get('available')
        modification_available = self.request.GET.get('modification_available')
        store = self.request.user.my_store
        qs = self.queryset.all()            
        
        id_list_default_excluded = [my_market.pk for my_market in Market.objects.filter(available=False)]

        for item in id_list_default_excluded:
            MarketModified.objects.get_or_create(
                market=Market.objects.get(pk=item),
                store = store,
                defaults = {
                    'available': False,
                    'modification_available': False
                }
            )

        if available is not None:             
            qs = qs.filter(my_modifications__store=store).filter(my_modifications__available=available) | qs.filter(available=available).exclude(my_modifications__store=store)
        if modification_available is not None:            
            if modification_available == 1:                                
                qs = qs.filter(my_modifications__store=store).filter(my_modifications__modification_available=modification_available)
            else:                                                
                qs = qs.filter(my_modifications__store=store).filter(my_modifications__modification_available=modification_available) | qs.all().exclude(my_modifications__store=store)

        return qs.distinct()



class MarketCotationView(CacheKeyDispatchMixin, ModelViewSet):
    queryset = Market.objects.none()
    serializer_class = MarketCotationSerializer    
    permission_classes = []    
    cache_group = 'market_cotation_view'
    caching_time = 60 * 5

    def get_queryset(self):
        game_id = self.request.GET.get('game_id')
        store = self.request.GET.get('store')        
        if not game_id:
            return Response({
                'success': False,
                'message': 'A ID do jogo é obrigatória'
            })

        id_list_excluded_markets = [excluded_markets.market.id for excluded_markets in MarketModified.objects.filter(available=False, store=store)]
        id_list_excluded_cotations = [excluded_cotations.cotation.id for excluded_cotations in CotationModified.objects.filter(available=False, store=store)]        
        
        id_list_default_excluded = [my_market.pk for my_market in Market.objects.filter(available=False)]
        id_list_allowed_markets = [my_market.market.pk for my_market in MarketModified.objects.filter(store=store, market__id__in=id_list_default_excluded, available=True)]
        

        for item in id_list_allowed_markets:
            if item in id_list_default_excluded:
                id_list_default_excluded.remove(item)
        
        for item in id_list_default_excluded:
            if item not in id_list_excluded_markets:
                id_list_excluded_markets.append(item)
    
        my_cotations_qs = Cotation.objects.filter(game=game_id).exclude(Q(market__name='1X2') | Q(pk__in=id_list_excluded_cotations))        
        for market_removed in MarketRemotion.objects.filter(store=store):                                   
            my_cotations_qs = my_cotations_qs.exclude(market__pk=market_removed.market_to_remove, name__regex=r'^.*?'+market_removed.under_above+'.*?'+market_removed.base_line+'.*?$')
        queryset = Market.objects.prefetch_related(Prefetch('cotations', queryset=my_cotations_qs, to_attr='my_cotations')).exclude(id__in=id_list_excluded_markets)
        queryset = queryset.annotate(cotations_count=Count('cotations', filter=Q(cotations__game__pk=game_id))).filter(cotations_count__gt=0).exclude(name='1X2')
        return queryset
        