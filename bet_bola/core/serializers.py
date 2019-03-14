from rest_framework import serializers
from .models import *
from ticket.models import Ticket
from utils.models import GeneralConfigurations

class StoreSerializers(serializers.HyperLinkedModelSerializer):
	
	config = serializers.SlugRelatedField(queryset = GeneralConfigurations.objects.all(),slug_field='id')

	class Meta:
		model = Store
		fields = ('username','fantasy','creation_date','email','config')


class CotationHistorySerializers(serializers.HyperLinkedModelSerializer):	
	
	original_cotation = serializers.SlugRelatedField(queryset = Cotation.objects.all(),slug_field='name')
	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='id')
	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')

	class Meta:
		model = CotationHistory
		fields = ('original_cotation','ticket','name','start_price','price','game','market','line','base_line')


class SportSerializers(serializers.HyperLinkedModelSerializer):	

	class Meta:
		model = Sport
		fields = ('name')


class Game(serializers.HyperLinkedModelSerializer):
	league = serializers.SlugRelatedField(queryset = Leagu.objects.all(),slug_field='name')
	Location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')
	sport = serializers.SlugRelatedField(queryset = Sport.objects.all(),slug_field='name')

	class Meta:
		model = Game
		fields = ('name','start_date','league','location','sport','games_status','visible','can_be_modified_by_api')


class Location(serializers.HyperLinkedModelSerializer):

	class Meta:
		model = Location
		fields = ('name','priority','visible')


class Market(serializers.HyperLinkedModelSerializer):
	
	class Meta:
		model = Market
		fields = ('name','available')


class Cotation(serializers.HyperLinkedModelSerializer):
	
	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')

	class Meta:
		model = Cotation
		fields = ('name','start_price','price','game','settlement','status','market','line','base_line','last_update')




