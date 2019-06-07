from rest_framework import serializers
from utils.models import GeneralConfigurations

class GeneralConfigurationsSerializer(serializers.HyperlinkedModelSerializer):	

	class Meta:
		model = GeneralConfigurations
		fields = ('max_cotation_value','min_number_of_choices_per_bet','max_number_of_choices_per_bet','max_reward_to_pay','min_bet_value','max_bet_value','min_cotation_sum','max_cotation_sum','cotations_percentage','bonus_by_won_ticket','block_bets','auto_pay_punter')
