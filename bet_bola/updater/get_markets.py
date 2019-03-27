from core.models import Cotation, Game, Market
from .market_translations import MARKET_TRANSLATIONS

def cotation_with_header(cotations, market_name, game_id):
    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=cotation['header'] + ' ' + cotation['goals'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
                #defaults={'name': MARKET_TRANSLATIONS.get(market_name, market_name) }
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )

def cotation_with_header_opp(cotations, market_name, game_id):
    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=cotation['header'] + ' ' + cotation['opp'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
                #defaults={'name': MARKET_TRANSLATIONS.get(market_name, market_name) }
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )

def cotation_with_header_name(cotations, market_name, game_id):
    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=cotation['header'] + ' - ' + cotation['name'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
                #defaults={'name': MARKET_TRANSLATIONS.get(market_name, market_name) }
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )




def cotation_without_header(cotations, market_name, game_id):

    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=cotation['opp'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name)
                #defaults={'name': MARKET_TRANSLATIONS.get(market_name, market_name) }
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )



