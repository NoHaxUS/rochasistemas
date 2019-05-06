from rest_framework import serializers
from core.models import Store
from utils.models import MarketReduction, MarketRemotion

class MarketReductionSerializer(serializers.HyperlinkedModelSerializer):
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketReduction
		fields = ('market_to_reduct', 'reduction_percentual', 'store')


class MarketRemotionSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('market_to_remove','below_above','base_line','store')

