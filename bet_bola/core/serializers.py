from django.db.models import Count
from rest_framework import serializers
from .models import *
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


class GameSerializer(serializers.HyperlinkedModelSerializer):		

	league = serializers.SlugRelatedField(queryset = League.objects.all(),slug_field='name')	
	sport = serializers.SlugRelatedField(queryset = Sport.objects.all(),slug_field='name')

	class Meta:
		model = Game
		fields = ('id','name','start_date','league','sport','game_status','visible','can_be_modified_by_api')


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

#Extra Serializers

class MinCotationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Cotation
		fields = ('id','name','price')


class LeagueGameTodaySerializers(serializers.HyperlinkedModelSerializer):
	# games = serializers.SerializerMethodField()
	league = serializers.CharField(source='name')
	location = serializers.SlugRelatedField(queryset=Location.objects.all(), slug_field='name')

	class Meta:
		model = League
		fields = ('id','league','location')


	# def get_games(self, league):		
	# 	qs = Game.objects.filter(league=league,start_date__gt=tzlocal.now(), 
 #        start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
 #        game_status__in=[1,8,9],
 #        visible=True)
        
	# 	serializer = LeagueGameSerializers(qs,many=True)
	# 	return serializer.data

class LeagueGameSerializers(serializers.HyperlinkedModelSerializer):			

	standard_cotations = MinCotationSerializer(many=True)
	league = LeagueGameTodaySerializers()

	class Meta:
		model = Game
		fields = ('id','name','start_date','game_status','league','standard_cotations')


class CountryGameTodaySerializers(serializers.HyperlinkedModelSerializer):
	itens = LeagueGameTodaySerializers(many=True, source='my_leagues')

	class Meta:
		model = Location
		fields = ('id','name','itens')	