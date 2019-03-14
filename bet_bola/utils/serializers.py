from rest_framework import serializers
from user.models import Seller
from core.models import Store
from .models import *


class ComissionSerializer(serializers.HyperLinkedModelSerializer):
	
	seller_related = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Comission
		fields = ('seller_related','simple','double','triple','fourth','fifth','sixth','sixth_more')


class GeneralConfigurationsSerializer(serializers.HyperLinkedModelSerializer):

	class Meta:
		model = GeneralConfigurations
		fields = ('max_cotation_value','min_number_of_choices_per_bet','max_reward_to_pay','min_bet_value','max_bet_value','min_cotation_sum','max_cotation_sum','percentual_reduction','block_bets','auto_pay_punter')


class RewardRelatedSerializer(serializers.HyperLinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = RewardRelated
		fields = ('value_max','reward_value_max','store')


class TicketCustomMessageSerializer(serializers.HyperLinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  TicketCustomMessage
		fields = ('text','store')


class RulesMessageSerializer(serializers.HyperLinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  RulesMessage
		fields = ('text','store')


class OverviewSerializer(serializers.HyperLinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  Overview
		fields = ('overview','store')


class MarketRemotionSerializer(serializers.HyperLinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('market_to_remove','below_above','base_line','store')



