import requests
from core.models import Game, Cotation, Championship, BetTicket, Country, Market
from utils.models import GeneralConfigurations
import utils.timezone as tzlocal
import datetime
from django.db.models import Count
from django.db.models import F, Q
import time
from decimal import Decimal
from .processing import processing_cotations_v2, process_tickets

from .choices import (MARKET_ID, MARKET_NAME_SMALL_TEAMS, 
    INVALID_ALL_COTES_CHAMPIONSHIPS, COUNTRY_TRANSLATE,
    not_allowed_championships
    )
from .aux_functions import (get_country_translated, 
    check_request_status, 
    renaming_cotations, 
    get_bet365_from_bookmakers, 
    can_save_this_market,
    set_cotations_reductions)



TOKEN = 'mnbJyKIOgJPb2LEQ1lCYolm8kKfhAJoQWkwqVhsD9dO48vhFPZw0F8CVDHQf'


def consuming_championship_api():

    print('Atualizando Campeonatos')
    request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
                           TOKEN + "&include=country&tz=America/Santarem")
    check_request_status(request)

    process_json_championship(request.json())
    total_pages = request.json().get('meta')['pagination']['total_pages']

    for actual_page in range(1, total_pages):
        request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
                               TOKEN + "&include=country&tz=America/Santarem&page=" + str(actual_page + 1))
        
        process_json_championship(request.json())
    consuming_game_cotation_api()



def consuming_game_cotation_api():

    before_time = tzlocal.now() - datetime.timedelta(days=3)

    before_year = before_time.year
    before_month = before_time.month
    before_day = before_time.day
    
    after_time = tzlocal.now() + datetime.timedelta(days=3)

    after_year = after_time.year
    after_month = after_time.month
    after_day = after_time.day


    first_date = str(before_year) + "-" + str(before_month) + "-" + str(before_day)
    second_date = str(after_year) + "-" +str(after_month) + "-" + str(after_day)


    print("Atualizando os Games")
    request = requests.get(
        'https://soccer.sportmonks.com/api/v2.0/fixtures/between/' + first_date + '/' + second_date + '?api_token=' + TOKEN + '&include=localTeam,visitorTeam,odds&tz=America/Santarem')
    total_pages = request.json().get('meta')['pagination']['total_pages']
    check_request_status(request)
    process_json_games_cotations(request.json())

    for actual_page in range(1, total_pages):
        next = 'https://soccer.sportmonks.com/api/v2.0/fixtures/between/' + first_date + '/' + second_date + '?page=' + \
            str(actual_page + 1) + '&api_token=' + TOKEN + \
            '&include=localTeam,visitorTeam,odds&tz=America/Santarem'
        request = requests.get(next)
        process_json_games_cotations(request.json())
    
    processing_cotations_v2()
    process_tickets()
    set_cotations_reductions()
    


def process_json_championship(json_response):

    championship_array = json_response.get('data')
    if championship_array:
        for championship in championship_array:                                    
            id_country = championship['country']['data']['id']

            if championship['id'] in not_allowed_championships:
                continue
            else:
                if not Country.objects.filter(pk=id_country).exists():                
                    country = Country.objects.create(pk=championship['country']['data']['id'], name=championship['country']['data']['name'])
                else:
                    country = Country.objects.get(pk=id_country)
                Championship(pk=championship['id'], name=championship['name'],
                                country=country).save()
    else:
        print("O array de campeonatos retornou vazio.")



def process_json_games_cotations(json_response):
    
    if GeneralConfigurations.objects.filter(pk=1):
        max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
    else:
        max_cotation_value = 200

    games_array = json_response.get('data')
    for game in games_array:

        if game["league_id"] in not_allowed_championships:
            continue
        else:
            if Game.objects.filter(pk=game['id']).exists():

                ft_score = game['scores']['ft_score']
                if not ft_score:
                    ft_score = F('ft_score')

                ht_score = game['scores']['ht_score']
                if not ht_score:
                    ht_score = F('ht_score')
                
                if not game.get('localTeam', None) or not game.get('visitorTeam', None):
                    continue

                Game.objects.filter(pk=game['id']).update(
                    name=get_country_translated(game['localTeam']['data']['name']) +
                    " x " + get_country_translated(game['visitorTeam']['data']['name']),
                    status_game=game['time']['status'],                
                    ht_score=ht_score,
                    ft_score=ft_score,
                    start_game_date=datetime.datetime.strptime(
                    game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
                    championship=Championship.objects.get(pk=game["league_id"])
                )
            else:
                if not game.get('localTeam', None) or not game.get('visitorTeam', None):
                    continue
                    
                Game.objects.create(
                    pk=game['id'],
                    name=get_country_translated(game['localTeam']['data']['name']) +
                    " x " + get_country_translated(game['visitorTeam']['data']['name']),
                    status_game=game['time']['status'],                
                    ht_score=game['scores']['ht_score'],
                    ft_score=game['scores']['ft_score'],
                    start_game_date=datetime.datetime.strptime(
                    game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
                    championship=Championship.objects.get(pk=game["league_id"])
                )
            save_odds(game['id'], game['odds'], max_cotation_value)



def save_odds(game_id, odds, max_cotation_value):

    odds_array = odds.get('data')
    game_instance = Game.objects.get(pk=game_id)
    championship_id = game_instance.championship_id

    processed_markets = []

    for market in odds_array:

        kind_name = MARKET_ID.get(market['id'], None)
        
        if not kind_name:
            continue
        else:
            if not Market.objects.filter(pk=int(market['id'])).exists():
                market_instance = Market.objects.create(pk=int(market['id']), name=kind_name)
            else:
                market_instance = Market.objects.get(pk=int(market['id']))

            if can_save_this_market(kind_name, championship_id, processed_markets):            
                bookmakers = market['bookmaker']['data']
                bookmaker = get_bet365_from_bookmakers(bookmakers)
                cotations = bookmaker['odds']['data']

                for cotation in cotations:

                    cotation_value = max_cotation_value if Decimal(cotation['value']) > max_cotation_value else Decimal(cotation['value'])
                    cotation_name_renamed = renaming_cotations(cotation['label']).strip()
                    total_or_none = None if cotation['total'] == None else cotation['total'].strip()
                    
                    if total_or_none:
                        cotation_name = cotation_name_renamed +" "+ total_or_none
                    else:
                        cotation_name = cotation_name_renamed

                    is_standard=False
                    if market_instance.pk == 1:
                        is_standard=True

                    cotation_total = cotation['total']

                    if not cotation_total == None:
                        if len(cotation_total.split(',')) > 1:
                            continue
                    

                    Cotation(
                        name=cotation_name,
                        value=cotation_value,
                        original_value=cotation_value,
                        game=game_instance,
                        is_standard=is_standard,
                        total=cotation_total,
                        kind=market_instance
                    ).save()
                    
                processed_markets.append(kind_name)


