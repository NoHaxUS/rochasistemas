from rest_framework import serializers
from core.models import Market
from core.serializers.cotation import MinimumCotationSerializer

class MarketCotationSerializer(serializers.HyperlinkedModelSerializer):
	cotations = serializers.SerializerMethodField()
	
	class Meta:
		model = Market
		fields = ('id','name','cotations')

	def get_cotations(self, market):
		serializer = MinimumCotationSerializer(market.my_cotations,many=True,context={'context':self.context})
		return serializer.data


class MarketSerializer(serializers.HyperlinkedModelSerializer):	
	reduction = serializers.SerializerMethodField()

	class Meta:
		model = Market
		fields = ('id','name','reduction')	
	
	def get_reduction(self, market):
		if market.my_reduction.exists():			
			return market.my_reduction.first().reduction_percentual
		return 0