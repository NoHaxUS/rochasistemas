from django.db.models import Count
from rest_framework import serializers
from .models import Store, CotationHistory, Sport, Game, League, Location, Market, Cotation
from ticket.models import Ticket
from user.models import CustomUser
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
		game_id = self.context['request'].GET.get('cotations__game__id')
		data = data.filter(game__id=game_id)
		return super(FilteredCotationSerializer, self).to_representation(data)


class CotationSerializer(serializers.HyperlinkedModelSerializer):

	game = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = Cotation
		list_serializer_class = FilteredCotationSerializer
		fields = ('id','name','game','price','line','base_line')

class CotationTicketSerializer(serializers.HyperlinkedModelSerializer):

	game = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = Cotation		
		fields = ('id','name','game','price','line','base_line')

class MarketSerializer(serializers.HyperlinkedModelSerializer):
	cotations = CotationSerializer(many=True)
	
	class Meta:
		model = Market
		fields = ('id','name','cotations')


class MinimumListCotationSerializer(serializers.ListSerializer):

	def to_representation(self, data):
		#print(data)
		store_id =  self.context['request'].GET.get('store')
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


class LeagueGameTodaySerializer(serializers.HyperlinkedModelSerializer):
	league = serializers.CharField(source='name')
	location = serializers.SlugRelatedField(queryset=Location.objects.all(), slug_field='name')

	class Meta:
		model = League
		fields = ('id','league','location')



class GameListSerializer(serializers.ListSerializer):

	def to_representation(self, data):
		
		#store_id =  self.context['request'].GET.get('store')
		return super(GameListSerializer, self).to_representation(data)

class GameSerializer(serializers.HyperlinkedModelSerializer):			

	standard_cotations = MinimumCotationSerializer(many=True)
	league = LeagueGameTodaySerializer()

	class Meta:
		model = Game
		list_serializer_class = GameListSerializer
		fields = ('id','name','start_date','game_status','league','standard_cotations')


class CountryGameTodaySerializers(serializers.HyperlinkedModelSerializer):
	itens = LeagueGameTodaySerializer(many=True, source='my_leagues')

	class Meta:
		model = Location
		fields = ('id','name','itens')	