"""
from core.models import Location, League, Sport, Market, Period, Game, Cotation
from django.utils.dateparse import parse_datetime
import datetime

def change_time_by_hours(date):

    current_date = parse_datetime(date)
    delta = datetime.timedelta(hours=2)
    real_date = current_date - delta
    return real_date

def get_game_name(participants):
    return participants[0]['Name'] + ' x ' + participants[1]['Name'] if int(participants[0]['Position']) == 1 else participants[1]['Name'] + ' x ' + participants[0]['Name']


def process_fixture_metadata(content):
    print("process_fixture_metadata")
    for game in content.get('Body')['Events']:
        fixture = game['Fixture']

        if game['FixtureId'] and fixture['Sport'] and fixture['Location'] and fixture['League']:

            game_name = get_game_name(fixture['Participants'])
            
            Game.objects.filter(pk=game['FixtureId']).update(
                name=game_name,
                start_date=change_time_by_hours(fixture['StartDate']),
                game_status=fixture['Status'],
                #league=League.objects.get_or_create(pk=fixture['League']['Id'], defaults={'name':fixture['League']['Name']})[0],
                #location=Location.objects.get_or_create(pk=fixture['Location']['Id'], defaults={'name': fixture['Location']['Name']})[0],
                #sport=Sport.objects.get_or_create(pk=fixture['Sport']['Id'], defaults={'name': fixture['Sport']['Name']})[0],
                last_update=fixture['LastUpdate']
            )



def process_markets_realtime(content):
    print("process_markets_realtime")
    for game in content.get('Body')['Events']:

        for market in game['Markets']:
            for cotation in market['Providers'][0]['Bets']:
                Cotation.objects.filter(id=cotation['Id']).update(
                    #name=cotation['Name'],
                    line=cotation.get('Line',None),
                    base_line=cotation.get('BaseLine', None),
                    status=cotation['Status'],
                    #start_price=cotation['StartPrice'],
                    price=cotation['Price'],
                    #settlement=cotation.get('Settlement',None),
                    last_update=cotation['LastUpdate']
                )


def process_settlements(content):
    print("process_settlements")
    for game in content.get('Body')['Events']:
        for market in game['Markets']:
            for cotation in market['Providers'][0]['Bets']:
                
                Cotation.objects.filter(id=cotation['Id']).update(
                    status=cotation['Status'],
                    settlement=cotation.get('Settlement', None),
                    last_update=cotation['LastUpdate']
                )
"""