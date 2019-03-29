def general_configurations(store):    
    from .models import GeneralConfigurations
    try:            
        general_config = GeneralConfigurations.objects.get(store=store)
        if general_config.max_reward_to_pay:
            max_reward_to_pay = general_config.max_reward_to_pay
        else:
            max_reward_to_pay = 100000.0
        
        if general_config.min_number_of_choices_per_bet:
            min_number_of_choices_per_bet = general_config.min_number_of_choices_per_bet
        else:
            min_number_of_choices_per_bet = 1

        if general_config.max_number_of_choices_per_bet:
            max_number_of_choices_per_bet = general_config.max_number_of_choices_per_bet
        else:
            max_number_of_choices_per_bet = 50

        if general_config.min_bet_value:
            min_bet_value = general_config.min_bet_value
        else:
            min_bet_value = 1

        if general_config.alert_bet_value:
            alert_bet_value = general_config.alert_bet_value
        else:
            alert_bet_value = 1000      

        if general_config.max_bet_value:
            max_bet_value = general_config.max_bet_value
        else:
            max_bet_value = 10000

    except GeneralConfigurations.DoesNotExist:
        alert_bet_value = 1000
        max_reward_to_pay = 100000.0
        min_number_of_choices_per_bet = 1
        max_number_of_choices_per_bet = 50
        min_bet_value = 1

    return {"max_reward_to_pay":max_reward_to_pay,"min_number_of_choices_per_bet":min_number_of_choices_per_bet,"max_number_of_choices_per_bet":max_number_of_choices_per_bet,"min_bet_value":min_bet_value, "max_bet_value":max_bet_value, "alert_bet_value":alert_bet_value}