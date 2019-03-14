from rest_framework import serializers
from .models import *
from ticket.models import Ticket
from user.models import CustomUser
from utils.models import GeneralConfigurations

class StoreSerializer(serializers.HyperlinkedModelSerializer):
	owner = serializers.SlugRelatedField(queryset = CustomUser.objects.all(),slug_field='id')
	config = serializers.SlugRelatedField(queryset = GeneralConfigurations.objects.all(),slug_field='id')

	class Meta:
		model = Store
		fields = ('owner','fantasy','creation_date','email','config')


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


class GameSerializer(serializers.HyperlinkedModelSerializer):		

	league = serializers.SlugRelatedField(queryset = League.objects.all(),slug_field='name')
	Location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')
	sport = serializers.SlugRelatedField(queryset = Sport.objects.all(),slug_field='name')

	class Meta:
		model = Game
		fields = ('name','start_date','league','location','sport','games_status','visible','can_be_modified_by_api')


class LeagueSerializer(serializers.HyperlinkedModelSerializer):

	Location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')

	class Meta:
		model = League
		fields = ('name','location','priority','visible')


class LocationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Location
		fields = ('name','priority','visible')


class MarketSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Market
		fields = ('name','available')


class CotationSerializer(serializers.HyperlinkedModelSerializer):
	
	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')

	class Meta:
		model = Cotation
		fields = ('name','start_price','price','game','settlement','status','market','line','base_line','last_update')



#Extra Serializers