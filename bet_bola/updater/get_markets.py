from core.models import Cotation
from .market_translations import MARKET_TRANSLATIONS

def goals_over_under(cotations, market_name, game_id):

    for cotation in cotations:
        obj, created = Cotation.objects.update_or_create(
            name=cotation['header'],
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
                defaults={'name': MARKET_TRANSLATIONS.get(market_name, market_name) }
            )[0],
            defaults={
                
            }
        )[0]

