from rest_framework.response import Response
from rest_framework import serializers
from core.models import Store,CotationCopy, CotationModified, Game, Market, Cotation
from ticket.models import Ticket
import utils.timezone as tzlocal
from django.utils import timezone

class FilteredCotationSerializer(serializers.ListSerializer):

	def to_representation(self, data):			
		game_id = self.context['request'].GET.get('game_id')

		if not game_id:
			raise serializers.ValidationError({'game_id': ['this field was not inserted']})
		if not Game.objects.filter(pk=game_id):
			raise serializers.ValidationError({'game_id': ['game does not exist']})

		game_id = self.context['request'].GET.get('game_id')
		data = data.filter(game__id=game_id)		

		store_id =  self.context['request'].GET.get('store')
		store = Store.objects.get(pk=store_id)
		config = store.config
		lista = list()
		print(data)
		if config:
			if config.cotations_percentage:			
				for cotation in data.all():
					cotation.price = (cotation.price * config.cotations_percentage / 100)	
					lista.append(cotation)
		
		return super(FilteredCotationSerializer, self).to_representation(lista)


class CotationGameSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Game
		fields = ('id','name','start_date')	


class CotationTicketSerializer(serializers.HyperlinkedModelSerializer):	

	game = CotationGameSerializer()
	market = serializers.SlugRelatedField(read_only=True, slug_field='name')	
	settlement = serializers.SerializerMethodField()

	class Meta:
		model = Cotation		
		fields = ('id','name','market','price','settlement','game')	

	def get_settlement(self, obj):
		return obj.get_settlement_display()


class MinimumListCotationSerializer(serializers.ListSerializer):

	def to_representation(self, data):			
		store_id = ''
		
		if self.root.context.get('request'):
			store_id =  self.root.context['request'].GET.get('store')			
		if self.root.context.get('context'):
			store_id =  self.root.context['context']['request'].GET.get('store')			

		store = Store.objects.get(pk=store_id)
		config = store.config
		if config:
			if config.cotations_percentage:
				for cotation in data:					
					if CotationModified.objects.filter(cotation=cotation, store=store):
						cotation.price = CotationModified.objects.filter(cotation=cotation, store=store).first().price
					else:
						cotation.price = (cotation.price * config.cotations_percentage / 100)

		return super(MinimumListCotationSerializer, self).to_representation(data)


class MinimumCotationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Cotation
		list_serializer_class = MinimumListCotationSerializer
		fields = ('id','name','price')



class CotationSerializer(serializers.HyperlinkedModelSerializer):
	game = serializers.SlugRelatedField(read_only=True, slug_field='name')
	market = serializers.SlugRelatedField(read_only=True, slug_field='name')
	settlement = serializers.SerializerMethodField()

	def get_settlement(self, cotation):
		return cotation.get_settlement_display()

	class Meta:
		model = Cotation
		fields = ('id','name','start_price','price','market','game','settlement')




class CotationModifiedSerializer(serializers.HyperlinkedModelSerializer):
	cotation = serializers.SlugRelatedField(queryset=Cotation.objects.all(), slug_field='id')
	store = serializers.SlugRelatedField(queryset=Store.objects.all(), slug_field='fantasy')

	class Meta:
		model = CotationModified	
		fields = ('cotation','price','store')



class CotationCopySerializer(serializers.HyperlinkedModelSerializer):	
	
	original_cotation = serializers.SlugRelatedField(queryset = Cotation.objects.all(), slug_field='name')
	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(), slug_field='id')
	game = serializers.SlugRelatedField(queryset = Game.objects.all(), slug_field='name')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(), slug_field='name')

	class Meta:
		model = CotationCopy
		fields = ('original_cotation','ticket','name','start_price','price','game','market','line','base_line')


