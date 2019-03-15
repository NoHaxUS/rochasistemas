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

TOKEN="20445-s1B9Vv6E9VSLU1"

def get_upcoming_events():
    today = datetime.datetime.today().strftime('%Y%m%d')
    #tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')
    page = 1
    url = "https://api.betsapi.com/v1/bet365/upcoming?sport_id=1&token=" + TOKEN + "&day=" + today + "&page=" + str(page)
    request = requests.get(url)
    process_upcoming_events(request.json())

def get_cc_from_result(game_id):
    url = "https://api.betsapi.com/v1/bet365/result?token=20445-s1B9Vv6E9VSLU1&event_id=" + game_id
    request = requests.get(url)
    data = request.json()
    if request.status_code == 200 and data['success'] == 1:
        return data['results']['league']['cc']


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
            )
        else:
            league.location = Location.objects.get_or_create(
                cc=cc,
                defaults={
                    'cc': cc,
                    'name': country_translated
                }
            )
        
        league.save()

        return league

def get_sport(game):
    sport = Sport.objects.get_or_create(
        pk=int(game['sport_id']),
        defaults={
            'name': SPORTS.get(game['sport_id'], "Futebol")
        }
    )
    return sport


def process_upcoming_events(data):
    if data['success'] == 1:
        for game in data['results']:
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






#-----#
def get_locations():
    print('Criando Localizações.')
    request = requests.get("http://prematch.lsports.eu/OddService/GetLocations?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")
    while not request.status_code == 200:
        request = requests.get("http://prematch.lsports.eu/OddService/GetLocations?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")
        time.sleep(5)
    process_locations(request.json())

def get_sports():
    print('Criando Sports.')
    request = requests.get("http://prematch.lsports.eu/OddService/GetSports?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")
    while not request.status_code == 200:
        request = requests.get("http://prematch.lsports.eu/OddService/GetSports?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")
        time.sleep(5)
    process_sports(request.json())

def get_leagues():
    print('Atualizando Ligas.')
    request = requests.get("http://prematch.lsports.eu/OddService/GetLeagues?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")
    while not request.status_code == 200:
        request = requests.get("http://prematch.lsports.eu/OddService/GetLeagues?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")
        time.sleep(5)
    #process_leagues(request.json())

def get_events():
    from_date = str(int((datetime.datetime.now() + datetime.timedelta(days=-1)).timestamp()))
    to_date = str(int((datetime.datetime.now() + datetime.timedelta(days=3)).timestamp()))
    #print("http://prematch.lsports.eu/OddService/GetEvents?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&FromDate="+from_date+"&ToDate="+to_date+"&Sports=6046")
    print("Atualizango Jogos e Cotas.")
    request = requests.get("http://prematch.lsports.eu/OddService/GetEvents?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&FromDate="+from_date+"&ToDate="+to_date+"&Sports=6046")
    while not request.status_code == 200:
        request = requests.get("http://prematch.lsports.eu/OddService/GetEvents?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&FromDate="+from_date+"&ToDate="+to_date+"&Sports=6046")
        time.sleep(5)
    process_events(request.json())


def process_locations(content):
    for location in content.get('Body'):
        if location['Id'] and location['Name']:
            Location.objects.update_or_create(
                pk=location['Id'],
                defaults={'name':COUNTRIES.get(str(location['Id']), location['Name'])}
            )

"""
def auto_pay_punter():
    if GeneralConfigurations.objects.filter(pk=1).exists():
        if GeneralConfigurations.objects.get(pk=1).auto_pay_punter:
            tickets = Ticket.objects.annotate(cotations_open=Count('cotations__pk', filter=Q(cotations__status=1)) )\
            .annotate(cotations_not_winner=Count('cotations__pk', filter=Q(cotations__settlement__in=[1,3,4]) & ~Q(cotations__game__game_status__in = (4,5,6,7,8)) ) )\
            .filter(cotations_open=0, cotations_not_winner=0, payment__status_payment='Pago')\
            .exclude(reward__reward_status=Reward.REWARD_STATUS[1][1])

            for ticket in tickets:
                ticket.pay_winner_punter(ticket.payment.who_set_payment)


#UEFA Europa League
#UEFA Champions League
#Europa League
def get_real_league_id(league_id, league_name):

    league_set = {
        1628,
        1781,
        1782,
        1783,
        1785,
        1786,
        1787,
        1788,
        1789,
        1790,
        1791,
        1792,

        3174,
        3175,
        3176,
        3177,
        3179,
        3180,
        3181,
        3178,

        26754,
        26757,
        26758,
        26759,
        26760,
        26761,
        26762,
        26763,
        26771,
        26772,
        26773,
        26777
        }

    league_dict = {
        50000: {
            1628,
            1781,
            1782,
            1783,
            1785,
            1786,
            1787,
            1788,
            1789,
            1790,
            1791,
            1792},
        50001:{
            3174,
            3175,
            3176,
            3177,
            3179,
            3180,
            3181,
            3178},
        50002:{
            26754,
            26757,
            26758,
            26759,
            26760,
            26761,
            26762,
            26763,
            26771,
            26772,
            26773,
            26777}
        }

    league_name_new = {
        50000:"UEFA Europa League",
        50001:"UEFA Champions League",
        50002:"Europa League"
    }

    
    if league_id in league_set:
        for new_league_id in league_dict.keys():
            if league_id in league_dict[new_league_id]:
                return (new_league_id, league_name_new[new_league_id] )

    return (league_id, league_name)


def process_reductions():
    if GeneralConfigurations.objects.filter(pk=1).exists():
        print("Processando Redução de Cotas Geral")
        GeneralConfigurations.objects.get(pk=1).apply_reductions()
    
    for market_reduction in MarketReduction.objects.all():
        print("Processando Redução: " + str(market_reduction.market_to_reduct))
        market_reduction.apply_reductions()


def process_sports(content):
    for sport in content.get('Body'):
        if sport['Id'] and sport['Name']:
            Sport.objects.update_or_create(
                pk=sport['Id'],
                defaults={
                'name':sport['Name']
                }
            )    


def change_time_by_hours(date):

    current_date = parse_datetime(date)
    delta = datetime.timedelta(hours=3)
    real_date = current_date - delta
    return real_date


def get_game_name(participants):
    return participants[0]['Name'] + ' x ' + participants[1]['Name'] if int(participants[0]['Position']) == 1 else participants[1]['Name'] + ' x ' + participants[0]['Name']


def process_events(content):

    for game in content.get('Body'):
        fixture = game['Fixture']
        print(game['FixtureId'])
        if game['FixtureId'] and fixture['Sport'] and fixture['Location'] and fixture['League']:
            
            game_name = get_game_name(fixture['Participants'])

            league_id_new, league_name_new = get_real_league_id(fixture['League']['Id'], fixture['League']['Name'])
            location_original = Location.objects.update_or_create(pk=fixture['Location']['Id'], defaults={'name': COUNTRIES.get(str(fixture['Location']['Id']), fixture['Location']['Name']) })[0]
            
            game_instance = Game.objects.update_or_create(
                pk=game['FixtureId'],
                defaults={
                    'name':game_name,
                    'start_date': change_time_by_hours(fixture['StartDate']),
                    'game_status': fixture['Status'],
                    'league': League.objects.update_or_create(pk=league_id_new, defaults={'name': get_translated_league(str(league_id_new), league_name_new), 'location': location_original})[0],
                    'location' : location_original,
                    'sport' : Sport.objects.update_or_create(pk=fixture['Sport']['Id'], defaults={'name': fixture['Sport']['Name']})[0],
                    'last_update': fixture['LastUpdate']
                }
            )[0]
            
            if game['Livescore'] and game['Livescore'].get('Periods', None):
                for period in game['Livescore']['Periods']:
                    if int(period['Results'][0]['Position']) == 1:
                        home_score= period['Results'][0]['Value']
                        away_score= period['Results'][1]['Value']
                    else:
                        home_score= period['Results'][1]['Value']
                        away_score= period['Results'][0]['Value']                

                    Period(period_type=period['Type'],
                    is_fineshed=period['IsFinished'],
                    is_confirmed=period['IsConfirmed'],
                    home_score=home_score,
                    away_score=away_score,
                    game = game_instance
                    ).save()

            if game['Markets']:
                process_markets(game['Markets'], game_instance)                


NOT_ALLOWED_MARKETS = [161,305,129,95,11]

def process_markets(markets, game_instance):

    for market in markets:
        if int(market['Id']) in NOT_ALLOWED_MARKETS:
            continue
        for cotation in market['Providers'][0]['Bets']:
            Cotation(id=cotation['Id'],
                id_string=cotation['Id'],
                name=get_translated_cotation(market['Name'], cotation['Name']) ,
                game=game_instance,
                line=cotation.get('Line',None),
                base_line=cotation.get('BaseLine', None),
                status=cotation['Status'],
                start_price=cotation['StartPrice'],
                price=cotation['Price'],
                settlement=cotation.get('Settlement',None),
                market=Market.objects.get_or_create(pk=market['Id'], defaults={'name': get_translated_market(market['Name']) })[0],
                last_update=cotation['LastUpdate']
            ).save()

"""