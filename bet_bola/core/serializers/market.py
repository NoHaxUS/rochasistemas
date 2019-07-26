from rest_framework import serializers
from core.models import Market
from core.serializers.cotation import StandardCotationSerializer, CotationsFromMarketSerializer

class MarketCotationSerializer(serializers.HyperlinkedModelSerializer):
	cotations = serializers.SerializerMethodField()
	
	class Meta:
		model = Market
		fields = ('id','name','cotations')

	def get_cotations(self, market):
		serializer = CotationsFromMarketSerializer(market.my_cotations, many=True, context={'context':self.context})
		return serializer.data


class MarketSerializer(serializers.HyperlinkedModelSerializer):	
	my_reduction = serializers.SerializerMethodField()

	class Meta:
		model = Market
		fields = ('id','name','my_reduction')	
	
	def get_my_reduction(self, market):		
		store = self.context['request'].user.my_store
		if market.my_reduction.filter(store=store).exists():			
			return {"reduction":market.my_reduction.filter(store=store).first().reduction_percentual, "active": market.my_reduction.first().active}
		return {"reduction":100, "active":False}