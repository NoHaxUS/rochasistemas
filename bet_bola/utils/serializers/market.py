from rest_framework import serializers
from core.models import Store, Market
from utils.models import MarketReduction, MarketRemotion

class MarketReductionSerializer(serializers.HyperlinkedModelSerializer):
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')
	
	class Meta:
		model = MarketReduction
		fields = ('market', 'reduction_percentual', 'store')


class MarketRemotionSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('market_to_remove','below_above','base_line','store')

