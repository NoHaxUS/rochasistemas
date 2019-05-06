from rest_framework import serializers
from core.models import Store
from utils.models import RewardRelated

class RewardRelatedSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = RewardRelated
		fields = ('value_max','reward_value_max','store')

	def validate(self, data):        
		if data['value_max'] < 0:
			raise serializers.ValidationError("Valor não pode ser negativo")
		if data['reward_value_max'] < 0:
			raise serializers.ValidationError("Valor não pode ser negativo")

		return data

