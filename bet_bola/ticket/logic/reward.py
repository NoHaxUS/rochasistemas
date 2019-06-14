def get_reward_value(raw_reward_total, store):

    from utils.models import GeneralConfigurations, RewardRestriction

    try:
        general_config = GeneralConfigurations.objects.get(store=store)
        max_reward_to_pay = general_config.max_reward_to_pay
    except GeneralConfigurations.DoesNotExist:
        max_reward_to_pay = 1000000

    restrictions = RewardRestriction.objects.all().order_by('max_reward_value','pk')

    for restriction in restrictions:
        if self.ticket.bet_value <= restriction.bet_value and raw_reward_total > restriction.max_reward_value:
            if raw_reward_total > restriction.max_reward_value:
                return (True, max_reward_to_pay) if restriction.max_reward_value > max_reward_to_pay else (True, restriction.max_reward_value)
            else:
                return (True, max_reward_to_pay) if raw_reward_total > max_reward_to_pay else (False, raw_reward_total)

    return (True, max_reward_to_pay) if raw_reward_total > max_reward_to_pay else (False, raw_reward_total)
