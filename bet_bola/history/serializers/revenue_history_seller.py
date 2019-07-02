from rest_framework import serializers
from user.models import Seller
from core.models import Store
from history.models import RevenueHistorySeller


class RevenueHistorySellerSerializer(serializers.HyperlinkedModelSerializer):
	
    register_by = serializers.SlugRelatedField(read_only=True, slug_field='username')    
    seller = serializers.SlugRelatedField(read_only=True, slug_field='first_name')	

    class Meta:
        model = RevenueHistorySeller
        fields = ('id','register_by','seller','date','entry','comission','total_out','profit')