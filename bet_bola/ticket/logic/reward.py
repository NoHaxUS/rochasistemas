def value(self):
    from utils.models import GeneralConfigurations, RewardRestriction

    try:
        general_config = GeneralConfigurations.objects.get(pk=1)
        max_reward_to_pay = general_config.max_reward_to_pay
    except GeneralConfigurations.DoesNotExist:
        max_reward_to_pay = 1000000

    raw_reward_total = round(self.cotation_sum() * self.bet_value, 2)
    restrictions = RewardRestriction.objects.all().order_by('max_reward_value','pk')

    for restriction in restrictions:
        if self.ticket.bet_value <= restriction.bet_value and raw_reward_total > restriction.max_reward_value:
            
            if raw_reward_total > restriction.max_reward_value:
                if restriction.max_reward_value > max_reward_to_pay:
                    return max_reward_to_pay
                else:
                    return restriction.max_reward_value
            else:
                if raw_reward_total > max_reward_to_pay:
                    return max_reward_to_pay
                else:
                    return raw_reward_total

    if raw_reward_total > max_reward_to_pay:
        return max_reward_to_pay
    else:
        return raw_reward_total
