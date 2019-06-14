def general_configurations(store):    
    from .models import GeneralConfigurations
    
    try:            
        general_config = GeneralConfigurations.objects.get(store=store)
        
        max_reward_to_pay = general_config.max_reward_to_pay
        min_number_of_choices_per_bet = general_config.min_number_of_choices_per_bet
        max_number_of_choices_per_bet = general_config.max_number_of_choices_per_bet    
        min_bet_value = general_config.min_bet_value
        alert_bet_value = general_config.alert_bet_value
        max_bet_value = general_config.max_bet_value


    except GeneralConfigurations.DoesNotExist:
        alert_bet_value = 1000
        max_reward_to_pay = 1000000
        min_number_of_choices_per_bet = 1
        max_number_of_choices_per_bet = 50
        min_bet_value = 1
        max_bet_value = 100000

    return {
        "max_reward_to_pay":max_reward_to_pay,
        "min_number_of_choices_per_bet": min_number_of_choices_per_bet, 
        "max_number_of_choices_per_bet":max_number_of_choices_per_bet, 
        "min_bet_value":min_bet_value, 
        "max_bet_value":max_bet_value, 
        "alert_bet_value":alert_bet_value
    }