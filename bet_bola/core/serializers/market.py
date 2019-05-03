from rest_framework import serializers
from core.models import Market
from core.serializers.cotation import MinimumCotationSerializer

class MarketSerializer(serializers.HyperlinkedModelSerializer):
	cotations = serializers.SerializerMethodField()
	
	class Meta:
		model = Market
		fields = ('id','name','cotations')

	def get_cotations(self, market):
		serializer = MinimumCotationSerializer(market.my_cotations,many=True,context={'context':self.context})
		return serializer.data