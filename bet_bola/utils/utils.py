def no_repetition_list(seq):
    """
    Convert a list of itens repeated or not to a list of no repeated itens
    preserving the order.
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
