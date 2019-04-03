from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import Count
from .models import Store, CotationHistory, Sport, Game, League, Location, Market, Cotation
from ticket.models import Ticket
from user.models import CustomUser
import utils.timezone as tzlocal
from django.utils import timezone
from utils.models import GeneralConfigurations

class StoreSerializer(serializers.HyperlinkedModelSerializer):	
	config = serializers.SlugRelatedField(queryset = GeneralConfigurations.objects.all(),slug_field='id')

	class Meta:
		model = Store
		fields = ('fantasy','creation_date','config')


class CotationHistorySerializer(serializers.HyperlinkedModelSerializer):	
	
	original_cotation = serializers.SlugRelatedField(queryset = Cotation.objects.all(),slug_field='name')
	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='id')
	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')

	class Meta:
		model = CotationHistory
		fields = ('original_cotation','ticket','name','start_price','price','game','market','line','base_line')


class SportSerializer(serializers.HyperlinkedModelSerializer):	

	class Meta:
		model = Sport
		fields = ('name',)


class LeagueSerializer(serializers.HyperlinkedModelSerializer):

	location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')

	class Meta:
		model = League
		fields = ('id','name','location','priority','visible')


class LocationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Location
		fields = ('id','name','priority','visible')


class FilteredCotationSerializer(serializers.ListSerializer):

	def to_representation(self, data):			
		if not self.context['request'].GET.get('game_id'):
			raise serializers.ValidationError({'game_id': ['this field was not inserted']})

		game_id = self.context['request'].GET.get('game_id')
		data = data.filter(game__id=game_id)		

		store_id =  self.context['request'].GET.get('store')
		store = Store.objects.get(pk=store_id)
		config = store.config
		lista = list()

		if config:
			if config.cotations_percentage:			
				for cotation in data.all():
					cotation.price = (cotation.price * config.cotations_percentage / 100)	
					lista.append(cotation)
		
		return super(FilteredCotationSerializer, self).to_representation(lista)


class CotationSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Cotation
		list_serializer_class = FilteredCotationSerializer
		fields = ('id','name','price')
		

class CotationTicketSerializer(serializers.HyperlinkedModelSerializer):

	game = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = Cotation		
		fields = ('id','name','game','price')	


class MinimumListCotationSerializer(serializers.ListSerializer):

	def to_representation(self, data):			
		store_id =  self.root.context['context']['request'].GET.get('store')
		store = Store.objects.get(pk=store_id)
		config = store.config
		if config:
			if config.cotations_percentage:
				for cotation in data:
					cotation.price = (cotation.price * config.cotations_percentage / 100)

		return super(MinimumListCotationSerializer, self).to_representation(data)


class MinimumCotationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Cotation
		list_serializer_class = MinimumListCotationSerializer
		fields = ('id','name','price')


class MarketSerializer(serializers.HyperlinkedModelSerializer):
	cotations = CotationSerializer(many=True)
	
	class Meta:
		model = Market
		fields = ('id','name','cotations')


class GameSerializer(serializers.HyperlinkedModelSerializer):			

	standard_cotations = MinimumCotationSerializer(many=True)	
	league = serializers.SlugRelatedField(queryset=League.objects.all(), slug_field='name')

	class Meta:
		model = Game				
		fields = ('id','name','start_date','game_status','league','standard_cotations')	


class LeagueGameSerializer(serializers.HyperlinkedModelSerializer):
	league = serializers.CharField(source='name')
	location = serializers.SlugRelatedField(queryset=Location.objects.all(), slug_field='name')
	games = serializers.SerializerMethodField()

	class Meta:
		model = League
		fields = ('id','league','location','games')

	def get_games(self, league):	
		from utils.models import ExcludedGame, ExcludedLeague					
		qs = league.games
		
		serializer = GameSerializer(qs,many=True,context={'context':self.context})
		return serializer.data
	

class CountryGameTodaySerializers(serializers.HyperlinkedModelSerializer):
	itens = LeagueGameSerializer(many=True, source='my_leagues')

	class Meta:
		model = Location
		fields = ('id','name','itens')	