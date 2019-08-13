from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from user.permissions import IsAdmin
from utils.serializers.market import MarketModifiedSerializer, MarketRemotionSerializer, GetMarketRemotionSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import MarketModified, MarketRemotion
from utils.cache import invalidate_cache_group
import json

class MarketModifiedView(ModelViewSet):
    queryset = MarketModified.objects.all()
    serializer_class = MarketModifiedSerializer
    permission_classes = [IsAdmin,]

    def get_queryset(self):
        store = self.request.user.my_store
        return self.queryset.filter(store=store)


    def create(self, validated_data):
        data = self.request.data.get('data')        
        data = json.loads(data)
        market = {}
        serializer_data = []
        for name in data['markets']:			
            market['store'] = self.request.user.my_store.pk
            market['reduction_percentual'] = data['reduction_percentual']
            market['market'] = name						
            
            if data.get('available', None) is not None:				
                market['available'] = data['available']

            serializer = self.get_serializer(data=market)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            serializer_data.append(serializer.data)		
        headers = self.get_success_headers(serializer.data)
        
        invalidate_cache_group(['/market_cotations/'], self.request.user.my_store.pk) 
        
        return Response(serializer_data, status=status.HTTP_201_CREATED, headers=headers)


class MarketRemotionView(ModelViewSet):
    queryset = MarketRemotion.objects.all()	
    permission_classes = [IsAdmin,]

    def get_queryset(self):
        store = self.request.user.my_store
        return self.queryset.filter(store=store)


    def create(self, request, *args, **kwargs):
        data = request.data.get('data')    		
        if not data:
            data = "{}"
        data = json.loads(data)        
        data['store'] = self.request.user.my_store.pk
        serializer = self.get_serializer(data=data)               
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)                
        headers = self.get_success_headers(serializer.data)

        invalidate_cache_group(['/market_cotations/'], request.user.my_store.pk) 

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)    		

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetMarketRemotionSerializer
        return MarketRemotionSerializer