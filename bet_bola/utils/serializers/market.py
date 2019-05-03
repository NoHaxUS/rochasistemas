
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

