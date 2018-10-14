import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
#from core.models import Game, Cotation, Championship, BetTicket, Country, Market

from multiprocessing.pool import ThreadPool

def get_locations(actual_page):
    request = requests.get("http://prematch.lsports.eu/OddService/GetLocations?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&Lang=pt")
    process_locations(request.json())

def get_leagues():
    print('Atualizando Ligas.')
    request = requests.get("http://prematch.lsports.eu/OddService/GetLeagues?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&Lang=pt")
    process_leagues(request.json())


def process_locations(content):
    for location in content.body:
        if location['Id'] and locatation['Name']:
            Location(pk=location['Id'], 
            name=location['Name']).save()

def process_leagues(content):
    for league in content.body:
        if league['Id'] and league['Name'] and league['LocationId'] and league['SportId']:
            League(pk=league['Id'], 
            name=league['Name'], 
            location=Location.objects.get(pk=league['LocationId']), 
            sport=Sport.objects.get(pk=league['SportId'])
            ).save()



def get_events():

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

    print("Atualizango Jogos e Cotas")
    request = requests.get("http://prematch.lsports.eu/OddService/GetEvents?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&FromDate=1539540801&ToDate=1539627201&Lang=pt")
    process_events(request.json())


def process_events(content):

    for game in content.body:
        fixture = game['Fixture']
        if game['FixtureId'] and fixture['Sport'] and fixture['Location'] and game['Fixture']['League']:

            if fixture['Participants'][0]['Position'] == 1:
                game_name = fixture['Participants'][0]['Name'] + 'x' + fixture['Participants'][1]['Name']
            else:
                game_name = fixture['Participants'][1]['Name'] + 'x' + fixture['Participants'][0]['Name']

            periods = fixture['Periods']

            for period in periods:
                if period['Results'][0]['Position'] == 1:
                    home_score= period['Results'][0]['Value']
                    away_score= period['Results'][1]['Value']
                else:
                    home_score= period['Results'][1]['Value']
                    away_score= period['Results'][0]['Value']                


                Period(period_type=period['Type'],
                IsFinished=period['IsFinished'],
                IsConfirmed=period['IsConfirmed'],
                home_score=home_score,
                away_score=away_score
                ).save()

            Game(pk=game['FixtureId'], 
            location=Location.objects.get(fixture['Location']['Id']),
            league=League.objects.get(fixture['League']['Id']),
            sport=Sport.objects.get(fixture['Sport']['Id']),
            start_date=fixture['StartDate'],
            last_update=fixture['LastUpdate'],
            status=fixture['Status'],
            name=game_name
            ).save()

            process_markets(game['Markets'])



def process_markets(markets):
    for market in markets:

        obj, created = Market.objects.get_or_create(
            pk=market['Id'],
            name=market['Name']
        )

        for cotation in market['Providers'][0]['Bets']:
            Cotation(pk=cotation['Id'],
            name=cotation['Name'],
            status=cotation['Status'],
            start_price=cotation['StartPrice'],
            price=cotation['Price'],
            settlement=cotation['Settlement'],
            market=obj).save()
    











#processing_cotations_v2()
#process_tickets()
#set_cotations_reductions()
    
    

