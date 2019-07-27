from rest_framework import serializers
from core.models import Store
from utils.models import RewardRestriction

class RewardRestrictionSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(read_only=True, slug_field='id')

	class Meta:
		model = RewardRestriction
		fields = ('id','bet_value','max_reward_value','store')

	def validate(self, data):        
		if data['bet_value'] < 0:
			raise serializers.ValidationError("Valor não pode ser negativo")
		if data['max_reward_value'] < 0:
			raise serializers.ValidationError("Valor não pode ser negativo")

		return data

