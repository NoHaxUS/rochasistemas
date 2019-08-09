from rest_framework import serializers
from user.models import Seller
from core.models import Store
from history.models import SellerCashierHistory


class SellerCashierHistorySerializer(serializers.HyperlinkedModelSerializer):
    	
    register_by = serializers.SlugRelatedField(read_only=True, slug_field='username')    
    seller = serializers.SlugRelatedField(read_only=True, slug_field='first_name')	
    premio_out = serializers.SerializerMethodField() 
    
    def get_premio_out(self, obj):
        return obj.total_out - obj.comission - obj.bonus_premio

    class Meta:
        model = SellerCashierHistory
        fields = ('id','register_by','seller','date','entry','bonus_premio','premio_out','comission','total_out','profit')