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


class MarketSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Market
		fields = ('id','name','available')


class CotationSerializer(serializers.HyperlinkedModelSerializer):

	SETTLEMENT_STATUS = (
            (None, "Em Aberto"),
            (-1, "Cancelada"),
            (1, "Perdeu"),
            (2, "Ganhou"),
            (3, "Perdeu"), #(3, "Reembolso"),
            (4, "Perdeu"), #(4, "Metade Perdida"),
            (5, "Ganhou") #(5, "Metade Ganha")
        )

	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')
	settlement = serializers.ChoiceField(choices=Cotation.SETTLEMENT_STATUS, required=False)
	# price = serializers.DecimalField(max_digits=30, decimal_places=2)

	class Meta:
		model = Cotation
		fields = ('id','name','start_price','price','game','settlement','status','market','line','base_line','last_update')


#Extra Serializers