from rest_framework import serializers
from core.models import Store
from utils.models import GeneralConfigurations

class GeneralConfigurationsSerializer(serializers.ModelSerializer):	
	store = serializers.SlugRelatedField(read_only=True, allow_null=True, slug_field='id')

	class Meta:
		model = GeneralConfigurations
		fields = (
		'pk','store','max_cotation_value','min_number_of_choices_per_bet',
		'max_number_of_choices_per_bet','max_reward_to_pay','min_bet_value','max_bet_value',
		'min_cotation_sum','max_cotation_sum','cotations_percentage','bonus_by_won_ticket','block_bets',
		'auto_pay_winners'
		)

	def create(self, validated_data):		
		user = self.context['request'].user		
		store = user.my_store		
		general_configuration = GeneralConfigurations.objects.filter(store=store)
		
		if general_configuration.exists():
			general_configuration.update(**validated_data)
			return general_configuration.first()
		else:
			obj = GeneralConfigurations(**validated_data)
			obj.store = store				
			obj.save()
			return obj
			