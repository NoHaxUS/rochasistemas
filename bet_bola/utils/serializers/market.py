from rest_framework import serializers
from core.models import Store, Market
from utils.models import MarketReduction, MarketRemotion

class MarketReductionSerializer(serializers.HyperlinkedModelSerializer):
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')
	
	class Meta:
		model = MarketReduction
		fields = ('market', 'reduction_percentual', 'active', 'store')


class MarketRemotionSerializer(serializers.HyperlinkedModelSerializer):	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('market_to_remove','under_above','base_line','store')

	def validate(self, data):		
		if not MarketRemotion.objects.filter(market_to_remove=data['market_to_remove'], under_above=data['under_above'], base_line=data['base_line'],store=data['store']).exists():
			return data
		raise serializers.ValidationError("Essa remoção ja foi efetuada antes")


class GetMarketRemotionSerializer(serializers.HyperlinkedModelSerializer):
	market_to_remove = serializers.SerializerMethodField()
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('id','market_to_remove','under_above','base_line','store')
	
	def get_market_to_remove(self, obj):
		return obj.get_market_to_remove_display()