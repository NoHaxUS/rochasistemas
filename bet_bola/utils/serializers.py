from rest_framework import serializers
from user.models import Seller
from core.models import Store, Game, League
from .models import *


class ComissionSerializer(serializers.HyperlinkedModelSerializer):
	
	seller_related = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Comission
		fields = ('seller_related','simple','double','triple','fourth','fifth','sixth','sixth_more')

	def validate(self, value):
		if data['simple'] < 0 or data['simple'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['double'] < 0 or data['double'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['triple'] < 0 or data['triple'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['fourth'] < 0 or data['fourth'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['fifth'] < 0 or data['fifth'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['sixth'] < 0 or data['sixth'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['sixth_more'] < 0 or data['sixth_more'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')

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
	total_revenue = serializers.SerializerMethodField()
	total_out_money = serializers.SerializerMethodField()
	seller_out_money = serializers.SerializerMethodField()
	manager_out_money = serializers.SerializerMethodField()
	total_net_value = serializers.SerializerMethodField()

	class Meta:
		model =  Overview
		fields = ('overview','store','total_revenue','total_out_money','seller_out_money','manager_out_money','total_net_value')

	def get_total_revenue(self,obj):
		return obj.total_revenue()

	def get_total_out_money(self,obj):
		return obj.total_out_money()

	def get_seller_out_money(self,obj):
		return obj.seller_out_money()

	def get_manager_out_money(self,obj):
		return obj.manager_out_money()

	def get_total_net_value(self,obj):
		return obj.total_net_value()


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

