from rest_framework import serializers
from core.models import Store
from utils.models import GeneralConfigurations

class GeneralConfigurationsSerializer(serializers.ModelSerializer):	
    store = serializers.SlugRelatedField(read_only=True, allow_null=True, slug_field='id')


    def create(self, validated_data):
        store = self.context['request'].user.my_store		
        config = GeneralConfigurations.objects.filter(store=store)
        if config:
            config_instance = config.first()
            config.update(**validated_data)
            return config_instance
        else:
            obj = GeneralConfigurations(**validated_data)
            obj.store = store				
            obj.save()
            return obj
        
    class Meta:
        model = GeneralConfigurations
        fields = (
            'pk','store','max_cotation_value','min_number_of_choices_per_bet','add_league_to_ticket_print',
            'max_number_of_choices_per_bet','max_reward_to_pay','min_bet_value','max_bet_value','add_link_to_ticket_whats',
            'min_cotation_sum','max_cotation_sum','cotations_percentage','bonus_by_won_ticket','bonus_won_ticket','block_bets'
        )