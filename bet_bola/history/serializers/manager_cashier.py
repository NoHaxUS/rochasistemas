from rest_framework import serializers
from history.models import ManagerCashierHistory


class ManagerCashierHistorySerializer(serializers.HyperlinkedModelSerializer):	

    register_by = serializers.SlugRelatedField(read_only=True, slug_field='username')    
    manager = serializers.SlugRelatedField(read_only=True, slug_field='first_name')

    class Meta:
        model = ManagerCashierHistory				
        fields = ('id','register_by','manager','date','entry','comission','total_out','profit')
        