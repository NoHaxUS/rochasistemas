from rest_framework import serializers
from core.models import Market
from core.serializers.cotation import StandardCotationSerializer

class MarketCotationSerializer(serializers.HyperlinkedModelSerializer):
	cotations = serializers.SerializerMethodField()
	
	class Meta:
		model = Market
		fields = ('id','name','cotations')

	def get_cotations(self, market):
		serializer = StandardCotationSerializer(market.my_cotations,many=True,context={'context':self.context})
		return serializer.data


class MarketSerializer(serializers.HyperlinkedModelSerializer):	
	my_reduction = serializers.SerializerMethodField()

	class Meta:
		model = Market
		fields = ('id','name','my_reduction')	
	
	def get_my_reduction(self, market):
		if market.my_reduction.exists():			
			return {"reduction":market.my_reduction.first().reduction_percentual, "active": market.my_reduction.first().active}
		return {"reduction":100, "active":False}