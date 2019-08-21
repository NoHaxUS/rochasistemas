def sort_by_priority(item):
    if item.location.modifications:
        if item.modifications:
            return (item.location.modifications[0].priority, item.modifications[0].priority)
        else:
            return (item.location.modifications[0].priority, 1)
    else:
        if item.modifications:
            return (1, item.modifications[0].priority)
        else:
            return (1, 1)

def sort_by_priority_menu(item):
    if item.modifications:
        return item.modifications[0].priority
    else:
        return 1
