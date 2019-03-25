import requests
import time
import datetime
import pika
import json
from core.models import Location, League, Sport, Market, Game, Cotation
from ticket.models import Ticket
#from .real_time import process_fixture_metadata, process_markets_realtime, process_settlements
from .translations import get_translated_cotation, get_translated_market, get_translated_league
from utils.models import MarketReduction, GeneralConfigurations
from django.db.models import Q , Count
from django.utils.dateparse import parse_datetime
from .countries import COUNTRIES
import time
from .ccs import COUNTRIES
from .sports import SPORTS
import math

TOKEN="20445-s1B9Vv6E9VSLU1"

def get_upcoming_events():
    today = datetime.datetime.today().strftime('%Y%m%d')
    #tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')
    page = 1
    
    url_base = "https://api.betsapi.com/v1/bet365/upcoming?sport_id=1&token=" + TOKEN + "&day=" + today + "&page="
    url_page = "https://api.betsapi.com/v1/bet365/upcoming?sport_id=1&token=" + TOKEN + "&day=" + today + "&page=" + str(page)

    request = requests.get(url_page)
    data = request.json()
    process_upcoming_events(data)

    if request.status_code == 200 and data['success'] == 1:
        games_total = data['pager']['total']
        per_page = data['pager']['per_page']
        num_pages = math.ceil(int(games_total) / int(per_page))
    
    while page <= num_pages:
        #print(page)
        #print(num_pages)
        request = requests.get(url_base + str(page))
        process_upcoming_events(request.json())
        page += 1

def get_cc_from_result(game_id):
    url = "https://api.betsapi.com/v1/bet365/result?token=20445-s1B9Vv6E9VSLU1&event_id=" + game_id
    request = requests.get(url)
    print("cc_from_result " + game_id)
    data = request.json()
    if request.status_code == 200 and data['success'] == 1:
        league = data['results'][0].get('league', None)
        if league:
            return league.get('cc', None)
    else:
        print("Get CC from result Failed.")


def get_game_name(game):
    return game['home']['name'] + ' x ' + game['away']['name']

def get_start_date_from_timestamp(game):
    return datetime.datetime.fromtimestamp(int(game['time']))


def get_league_and_create_location(game):
    league, created = League.objects.get_or_create(
        pk=int(game['league']['id']),
        defaults={
            'name': game['league']['name']
        }
    )

    if league.location == None:
        cc = get_cc_from_result(game['id'])
        country_translated = COUNTRIES.get(cc, None)

        if cc == None or country_translated == None:
            league.location = Location.objects.get_or_create(
                cc="inter",
                defaults={
                    'cc': 'inter',
                    'name': COUNTRIES.get('inter', "Internacional")
                }
            )[0]
        else:
            league.location = Location.objects.get_or_create(
                cc=cc,
                defaults={
                    'cc': cc,
                    'name': country_translated
                }
            )[0]
        
        league.save()

        return league

def get_sport(game):
    sport = Sport.objects.get_or_create(
        pk=int(game['sport_id']),
        defaults={
            'name': SPORTS.get(game['sport_id'], "Futebol")
        }
    )[0]
    return sport


def process_upcoming_events(data):
    if data['success'] == 1:
        for game in data['results']:
            print(game['id'])
            game_obj, created = Game.objects.get_or_create(
                pk=game['id'],
                defaults={
                    'name': get_game_name(game),
                    'start_date': get_start_date_from_timestamp(game),
                    'league': get_league_and_create_location(game),
                    'sport': get_sport(game),
                    'game_status': int(game['time_status'])
                }
            )



def get_cotations(game_id):

    url = "https://api.betsapi.com/v1/bet365/start_sp?token=20445-s1B9Vv6E9VSLU1&FI=" + str(game_id)
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['success'] == 1:
        if data[0].get('goals', None): 
            get_goals_cotations(data[0]['goals'])



def get_goals_cotations
