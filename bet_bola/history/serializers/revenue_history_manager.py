from rest_framework import serializers
from history.models import RevenueHistoryManager


class RevenueHistoryManagerSerializer(serializers.HyperlinkedModelSerializer):	

    register_by = serializers.SlugRelatedField(read_only=True, slug_field='username')    
    manager = serializers.SlugRelatedField(read_only=True, slug_field='first_name')

    class Meta:
        model = RevenueHistoryManager				
        fields = ('id','register_by','manager','date','entry','comission','total_out','profit')
	
