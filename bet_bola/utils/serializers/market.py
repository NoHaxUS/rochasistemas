from rest_framework import serializers
from core.models import Store, Market
from utils.models import MarketModified, MarketRemotion

class MarketModifiedSerializer(serializers.HyperlinkedModelSerializer):
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	market = serializers.SlugRelatedField(queryset = Market.objects.all(),slug_field='name')
	
	def create(self, validated_data):
		user = self.context['request'].user		
		market = validated_data.get('market')		
		market_reductions = MarketModified.objects.filter(market__pk=market.pk, store=user.my_store)

		if market_reductions.exists():					
			market_reductions.update(**validated_data)			
			return market_reductions.first()

		instance = MarketModified(**validated_data)			
		instance.store = user.my_store		
		instance.save()		
		return instance

	def validate_market(self, market):
		if market.name == "1X2":
			raise serializers.ValidationError("Mercado 1X2 não pode ser indisponibilizado.")
		return market
	class Meta:
		model = MarketModified
		fields = ('market', 'reduction_percentual', 'active', 'store')


class MarketRemotionSerializer(serializers.HyperlinkedModelSerializer):	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = MarketRemotion	
		fields = ('market_to_remove','under_above','base_line','store')	

	def validate(self, data):		
		if not MarketRemotion.objects.filter(market_to_remove=data['market_to_remove'], under_above=data['under_above'], base_line=data['base_line'],store=self.context['request'].user.my_store).exists():
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