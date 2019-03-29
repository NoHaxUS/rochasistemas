from core.models import Cotation, Game, Market
from .market_translations import MARKET_TRANSLATIONS

def get_translated_cotation_with_header(cotation_name):
    TRANSLATE_TABLE = {
        'Over': 'Acima',
        'Under':'Abaixo',
        'Home':'Casa',
        'Away':'Fora',
        'X':'Empate',
    }
    cotation_translated = cotation_name.strip()
    for header in TRANSLATE_TABLE.keys():
        cotation_translated = cotation_translated.replace(header, TRANSLATE_TABLE.get(header, header))
    return cotation_translated


def get_translated_cotation_with_header_name(cotation_name):
    TRANSLATE_TABLE = {
        'Draw':'Empate',
        '2nd Half':'2° Tempo',
        '1st Half':'1° Tempo',
    }
    cotation_translated = cotation_name.strip()
    for header in TRANSLATE_TABLE.keys():
        cotation_translated = cotation_translated.replace(header, TRANSLATE_TABLE.get(header, header))
    return cotation_translated


def get_translated_cotation_with_opp(cotation_name):
    TRANSLATE_TABLE = {
        '1':'Casa',
        '2': 'Fora',
        'X':'Empate',
        '1X':'Casa/Empate',
        'X2':'Empate/Fora',
        '12':'Casa/Fora',
        'Over': 'Acima',
        'Under':'Abaixo',
        'Draw':'Empate',
        'Yes': 'Sim',
        'No': 'Não',
        'Goals':'Gols',
        'goals':'Gols',
        'Both Teams':'Ambos os Times',
        'Only':'Apenas',
        'No Goals': 'Sem Gols',
        '1st Half': '1° Tempo',
        '2nd Half': '2° Tempo',
        'Tie':'Igual',
        'Even': 'Par',
        'Odd':'Ímpar'
    }
    cotation_translated = cotation_name
    for header in TRANSLATE_TABLE.keys():
        cotation_translated = cotation_translated.replace(header, TRANSLATE_TABLE.get(header, header))
    return cotation_translated
    
}

def cotation_with_header(cotations, market_name, game_id):
    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=get_translated_cotation_with_header(cotation['header']) + ' ' + cotation['goals'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )


def cotation_with_header_opp(cotations, market_name, game_id):
    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=get_translated_cotation_with_header_opp(cotation['header']) + ' ' + cotation['opp'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )


def cotation_with_header_name(cotations, market_name, game_id):
    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=get_translated_cotation_with_header_name(cotation['header']) + ' - ' + cotation['name'],
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name),
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )


def cotation_without_header(cotations, market_name, game_id):

    for cotation in cotations:
        Cotation.objects.update_or_create(
            name=get_translated_cotation_with_header_opp(cotation['opp']),
            game=Game.objects.get(pk=game_id),
            market=Market.objects.get_or_create(
                name=MARKET_TRANSLATIONS.get(market_name, market_name)
            )[0],
            defaults={
                'price': cotation['odds'],
            }
        )



