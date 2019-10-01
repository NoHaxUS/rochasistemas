from rest_framework.response import Response
from rest_framework import serializers
from core.models import CotationCopy, CotationModified, Game, Market, Cotation, Store
from utils.models import GeneralConfigurations
from ticket.models import Ticket
import utils.timezone as tzlocal
from django.utils import timezone

class CotationGameSerializer(serializers.HyperlinkedModelSerializer):
    league = serializers.SlugRelatedField(read_only=True, slug_field='name')
    
    class Meta:
        model = Game        
        fields = ('id','name','start_date','league')	


class CotationTicketWithCopiedPriceSerializer(serializers.HyperlinkedModelSerializer):	

    game = CotationGameSerializer()
    market = serializers.SlugRelatedField(read_only=True, slug_field='name')	
    price = serializers.SerializerMethodField()
    settlement = serializers.SerializerMethodField()

    class Meta:
        model = Cotation		
        fields = ('id','name','market','price','settlement','game')	

    def get_settlement(self, obj):
        return obj.get_right_settlement_display()

    def get_price(self, obj):        
        cotation = CotationCopy.objects.filter(original_cotation=obj, ticket__pk=self.context['ticket_id']).first()
        return cotation.price


class CotationTicketSerializer(serializers.HyperlinkedModelSerializer):	

    game = CotationGameSerializer()
    market = serializers.SlugRelatedField(read_only=True, slug_field='name')	
    settlement = serializers.SerializerMethodField()

    class Meta:
        model = Cotation		
        fields = ('id','name','market','price','settlement','game')	

    def get_settlement(self, obj):
        return obj.get_right_settlement_display()


class MinimumListCotationSerializer(serializers.ListSerializer):
    def to_representation(self, data):

        if self.root.context.get('request'):
            store_id =  self.root.context['request'].GET.get('store')			
        if self.root.context.get('context'):
            store_id =  self.root.context['context']['request'].GET.get('store')
        
        store =  Store.objects.get(pk=store_id)
				
        for cotation in data:				
            cotation.price = cotation.get_store_price(store)
                    
        return super().to_representation(data)


class StandardCotationSerializer(serializers.HyperlinkedModelSerializer):
    market = serializers.SlugRelatedField(read_only=True, slug_field='name')
    available = serializers.SerializerMethodField()

    class Meta:
        model = Cotation
        list_serializer_class = MinimumListCotationSerializer
        fields = ('id','name','price','available','market')
    
    def get_available(self, cotation):				
        store_id = self.context['context']['request'].GET.get('store')		
        queryset = CotationModified.objects.filter(cotation=cotation, store__pk=store_id)
        if queryset:
            return queryset.first().available
        return True
        


class CotationsFromMarketSerializer(serializers.HyperlinkedModelSerializer):
    market = serializers.SlugRelatedField(read_only=True, slug_field='name')	

    class Meta:
        model = Cotation
        list_serializer_class = MinimumListCotationSerializer
        fields = ('id','name','price','market')		


class CotationSerializerForTable(serializers.HyperlinkedModelSerializer):
    market = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Cotation
        fields = ('id','name','price','market')



class CotationSerializer(serializers.HyperlinkedModelSerializer):
    game = serializers.SlugRelatedField(read_only=True, slug_field='name')
    market = serializers.SlugRelatedField(read_only=True, slug_field='name')
    settlement = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()

    def get_settlement(self, cotation):
        return cotation.get_right_settlement_display()

    class Meta:
        model = Cotation
        fields = ('id','name','price','original_price','market','available','game','settlement')

    def get_available(self, cotation):
        store_id = ''
        if self.root.context.get('request'):
            store =  self.root.context['request'].user.my_store			
        if self.root.context.get('context'):
            store =  self.root.context['context']['request'].user.my_store

        queryset = CotationModified.objects.filter(cotation=cotation, store=store)
        if queryset:
            return queryset.first().available
        return True

    def get_original_price(self, cotation):						
        return str(cotation.price)

    def get_price(self, cotation):		
        store = self.context['request'].user.my_store
        config = GeneralConfigurations.objects.filter(store=store).first()		
        if CotationModified.objects.filter(cotation=cotation, store=store) and CotationModified.objects.filter(cotation=cotation, store=store).first().price != 0:
            return str(CotationModified.objects.get(cotation=cotation, store=store).price)			

        return "-"


class CotationModifiedSerializer(serializers.HyperlinkedModelSerializer):
    cotation = serializers.SlugRelatedField(queryset=Cotation.objects.all(), slug_field='id')
    store = serializers.SlugRelatedField(read_only=True, slug_field='id')

    class Meta:
        model = CotationModified	
        fields = ('cotation','price','available','store')



class CotationCopySerializer(serializers.HyperlinkedModelSerializer):	
    
    original_cotation = serializers.SlugRelatedField(queryset = Cotation.objects.all(), slug_field='name')
    ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(), slug_field='id')
    game = serializers.SlugRelatedField(queryset = Game.objects.all(), slug_field='name')
    market = serializers.SlugRelatedField(queryset = Market.objects.all(), slug_field='name')

    class Meta:
        model = CotationCopy
        fields = ('original_cotation','ticket','price')


