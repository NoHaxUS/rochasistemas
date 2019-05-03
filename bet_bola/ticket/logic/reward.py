def real_value(self):
    from utils.models import GeneralConfigurations, RewardRelated
    try:
        general_config = GeneralConfigurations.objects.get(pk=1)
        max_reward_to_pay = general_config.max_reward_to_pay
    except GeneralConfigurations.DoesNotExist:
        max_reward_to_pay = 50000

    reward_total = round(self.ticket.value * self.ticket.cotation_sum(), 2)
    for reward_related in RewardRelated.objects.all().order_by('value_max','pk'):
        if self.ticket.value <= reward_related.value_max and reward_total > reward_related.reward_value_max:
            if reward_total > reward_related.reward_value_max:
                if reward_related.reward_value_max > max_reward_to_pay:
                    return max_reward_to_pay
                else:
                    return reward_related.reward_value_max
            else:
                if reward_total > max_reward_to_pay:
                    return max_reward_to_pay
                else:
                    return reward_total

    if reward_total > max_reward_to_pay:
        return max_reward_to_pay
    else:
        return reward_total
