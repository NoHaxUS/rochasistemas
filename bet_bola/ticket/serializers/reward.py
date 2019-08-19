from rest_framework import serializers
from ticket.models import Reward
from user.models import Seller

class RewardSerializer(serializers.HyperlinkedModelSerializer):
	who_rewarded_the_winner = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	

	class Meta:
		model = Reward
		fields = ('who_rewarded_the_winner','date','value')	

