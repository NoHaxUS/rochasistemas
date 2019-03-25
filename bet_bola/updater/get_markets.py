from core.models import Cotation
from .market_translations import MARKET_TRANSLATIONS

def goals_over_under(cotations, game_id):

    for cotation in cotations:
        obj, created = Cotation.objects.update_or_create(
            pk=cotation['']
        )[0]

