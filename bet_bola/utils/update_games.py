import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from core.models import Game, Cotation, Championship, BetTicket, Country, Market
from utils.models import GeneralConfigurations
import utils.timezone as tzlocal
import datetime
from django.db.models import Count
from django.db.models import F, Q
from decimal import Decimal
from .processing import processing_cotations_v2, process_tickets

from .choices import (MARKET_ID, MARKET_NAME_SMALL_TEAMS, 
    INVALID_ALL_COTES_CHAMPIONSHIPS, COUNTRY_TRANSLATE,
    NOT_ALLOWED_CHAMPIONSHIPS
    )
from .aux_functions import ( 
    check_request_status, 
    renaming_cotations, 
    get_bet365_from_bookmakers, 
    can_save_this_market,
    set_cotations_reductions
    )

from multiprocessing.pool import ThreadPool

TOKEN = 'lg9jUW7exqsIA9a2oEBwog3rW06l58pWoCLL9clqzA1TUG7kBjUQSghiGig3'

def error_callback(error):
    print(error)

def make_championship_request_async(actual_page):
    request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
        TOKEN + "&include=country&tz=America/Santarem&page=" + str(actual_page + 1))
    process_json_championship(request.json())

def consuming_championship_api():
    
    print('Atualizando Campeonatos')
    request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
                           TOKEN + "&include=country&tz=America/Santarem")
    check_request_status(request)

    response_data = request.json()

    pool = ThreadPool()
    pool.apply_async(process_json_championship, args=(response_data,), error_callback = error_callback)

    total_pages = request.json().get('meta')['pagination']['total_pages']
    
    for actual_page in range(1, total_pages):
        pool.apply_async(make_championship_request_async, args=(actual_page,), error_callback = error_callback)

    pool.close()
    pool.join()
    
    consuming_game_cotation_api()


def process_json_championship(json_response):
    
    championship_array = json_response.get('data')
    if championship_array:
        for championship in championship_array:                                    
            country_id = championship['country']['data']['id']

            championship_id = championship['id']
            championship_name = championship['name']
            if championship_id not in NOT_ALLOWED_CHAMPIONSHIPS:
                country_name = championship['country']['data']['name']
                if not Country.objects.filter(pk=country_id).exists():     
                    country = Country.objects.create(pk=country_id, name=country_name)
                else:
                    country = Country.objects.get(pk=country_id)
                
                Championship(pk=championship_id, name=championship_name, country=country).save()
    else:
        print("Error: The championship array is empty.")


def make_game_request_async(actual_page, first_date, second_date, max_cotation_value):
    next_url = 'https://soccer.sportmonks.com/api/v2.0/fixtures/between/' + first_date + '/' + second_date + '?page=' + \
        str(actual_page + 1) + '&api_token=' + TOKEN + '&include=localTeam,visitorTeam,odds&tz=America/Santarem'
    
    request = requests.get(next_url)
    request_data = request.json()
    process_json_games_cotations(request_data, max_cotation_value)


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
    request = requests.get('https://soccer.sportmonks.com/api/v2.0/fixtures/between/' + first_date + '/' + second_date + '?api_token=' + TOKEN + '&include=localTeam,visitorTeam,odds&tz=America/Santarem')
    
    total_pages = request.json().get('meta')['pagination']['total_pages']
    check_request_status(request)

    if GeneralConfigurations.objects.filter(pk=1).exists():
        max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
    else:
        max_cotation_value = 200

    request_data = request.json()

    pool = ThreadPool()
    pool.apply_async(process_json_games_cotations, args=(request_data, max_cotation_value), error_callback = error_callback)
    
    
    for actual_page in range(1, total_pages):
        pool.apply_async(make_game_request_async, args = (actual_page, first_date, second_date, max_cotation_value), error_callback = error_callback)

    
    pool.close()
    pool.join()
    
    processing_cotations_v2()
    process_tickets()
    set_cotations_reductions()
    
    


def process_json_games_cotations(json_response, max_cotation_value):
    
    games_array = json_response.get('data')
    for game in games_array:
        
        if game["league_id"] not in NOT_ALLOWED_CHAMPIONSHIPS:
            
            local_team = game.get('localTeam', None)
            visitor_team = game.get('visitorTeam', None)
            game_id = game['id']

            if local_team and visitor_team:
                if Game.objects.filter(pk=game_id).exists():
                    ft_score = game['scores']['ft_score']
                    if not ft_score:
                        ft_score = F('ft_score')

                    ht_score = game['scores']['ht_score']
                    if not ht_score:
                        ht_score = F('ht_score')
                    Game.objects.filter(pk=game_id).update(
                        status_game=game['time']['status'],                
                        ht_score=ht_score,
                        ft_score=ft_score
                    )
                else:
                    Game.objects.create(
                        pk=game['id'],
                        name=local_team['data']['name'] + " x " + visitor_team['data']['name'],
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

    processed_markets = set()

    for market in odds_array:
        market_id = market['id']
        kind_name = MARKET_ID.get(market['id'], None)
        
        if kind_name:
            if not Market.objects.filter(pk=market_id).exists():
                market_instance = Market.objects.create(pk=market_id, name=kind_name)
            else:
                market_instance = Market.objects.get(pk=market_id)

            if can_save_this_market(kind_name, championship_id, processed_markets):            
                bookmakers = market['bookmaker']['data']
                bookmaker = get_bet365_from_bookmakers(bookmakers)
                cotations = bookmaker['odds']['data']

                for cotation in cotations:
                    cotation_total = cotation['total']

                    if cotation_total and len(cotation_total.split(',')) > 1:
                        continue

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

                    Cotation(
                        name=cotation_name,
                        value=cotation_value,
                        original_value=cotation_value,
                        game=game_instance,
                        is_standard=is_standard,
                        total=cotation_total,
                        kind=market_instance
                    ).save()
                
                processed_markets.add(kind_name)


