from rest_framework import serializers
from user.models import Seller
from core.models import Store, Game, League
from .models import *


class ComissionSerializer(serializers.HyperlinkedModelSerializer):
	
	seller_related = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Comission
		fields = ('seller_related','simple','double','triple','fourth','fifth','sixth','sixth_more')


class GeneralConfigurationsSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = GeneralConfigurations
		fields = ('max_cotation_value','min_number_of_choices_per_bet','max_number_of_choices_per_bet','max_reward_to_pay','min_bet_value','max_bet_value','min_cotation_sum','max_cotation_sum','cotations_percentage','block_bets','auto_pay_punter')


class RewardRelatedSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = RewardRelated
		fields = ('value_max','reward_value_max','store')

	def validate(self, data):        
		if data['value_max'] < 0:
			raise serializers.ValidationError("Valor não pode ser negativo")
		if data['reward_value_max'] < 0:
			raise serializers.ValidationError("Valor não pode ser negativo")

		return data


class TicketCustomMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  TicketCustomMessage
		fields = ('text','store')


class RulesMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  RulesMessage
		fields = ('text','store')


class OverviewSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  Overview
		fields = ('overview','store')


class MarketRemotionSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('market_to_remove','below_above','base_line','store')


class ExcludedGameSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')

	class Meta:
		model = ExcludedGame
		fields = ('store','game')


class MarketReductionSerializer(serializers.HyperlinkedModelSerializer):
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketReduction
		fields = ('market_to_reduct', 'reduction_percentual', 'store')


class ExcludedLeagueSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(), slug_field='id')
	league = serializers.SlugRelatedField(queryset = League.objects.all(), slug_field='name')

	class Meta:
		model = ExcludedLeague	
		fields = ('store','league')

