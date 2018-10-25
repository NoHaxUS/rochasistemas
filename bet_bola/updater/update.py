import requests
import time
import datetime
import pika
import json
from core.models import Location, League, Sport, Market, Period, Game, Cotation
from .real_time import process_fixture_metadata, process_markets_realtime, process_settlements

def get_locations():
    request = requests.get("http://prematch.lsports.eu/OddService/GetLocations?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&Lang=pt")
    process_locations(request.json())

def get_sports():
    print('Criando Sports')
    request = requests.get("http://prematch.lsports.eu/OddService/GetSports?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&Lang=pt")
    process_sports(request.json())

def get_leagues():
    print('Atualizando Ligas.')
    request = requests.get("http://prematch.lsports.eu/OddService/GetLeagues?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&Lang=pt")
    process_leagues(request.json())

def get_events():
    from_date = str(int(time.time()))
    to_date = str(int((datetime.datetime.now() + datetime.timedelta(days=2)).timestamp()) )

    print("Atualizango Jogos e Cotas")
    request = requests.get("http://prematch.lsports.eu/OddService/GetEvents?Username=pabllobeg1@gmail.com&Password=cdfxscsdf45f23&Guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54&FromDate="+from_date+"&ToDate="+to_date+"&Lang=pt&Sports=6046")
    process_events(request.json())


def process_locations(content):
    for location in content.get('Body'):
        if location['Id'] and location['Name']:
            Location(
                pk=location['Id'], 
                name=location['Name']
            ).save()

def process_leagues(content):
    for league in content.get('Body'):
        if league['Id'] and league['Name'] and league['LocationId'] and league['SportId']:
            League(pk=league['Id'], 
            name=league['Name'],
            location=Location.objects.get(pk=league['LocationId'])                         
            ).save()

def process_sports(content):
    for sport in content.get('Body'):
        if sport['Id'] and sport['Name']:
            Sport(
                pk=sport['Id'],
                name=sport['Name']
                ).save()    


def get_game_name(participants):
    return participants[0]['Name'] + ' x ' + participants[1]['Name'] if int(participants[0]['Position']) == 1 else participants[1]['Name'] + ' x ' + participants[0]['Name']

def process_events(content):

    for game in content.get('Body'):
        fixture = game['Fixture']
        print(game['FixtureId'])
        if game['FixtureId'] and fixture['Sport'] and fixture['Location'] and fixture['League']:

            game_name = get_game_name(fixture['Participants'])
            
            game_instance = Game.objects.get_or_create(
                pk=game['FixtureId'],
                defaults={
                    'name':game_name,
                    'start_date': fixture['StartDate'],
                    'game_status': fixture['Status'],
                    'league': League.objects.get_or_create(pk=fixture['League']['Id'], defaults={'name':fixture['League']['Name']})[0],
                    'location' : Location.objects.get_or_create(pk=fixture['Location']['Id'], defaults={'name': fixture['Location']['Name']})[0],
                    'sport' : Sport.objects.get_or_create(pk=fixture['Sport']['Id'], defaults={'name': fixture['Sport']['Name']})[0],
                    'last_update': fixture['LastUpdate']
                }
            )[0]
            
            if game['Livescore'] and game['Livescore'].get('Periods',None):
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


REAL_COTATION_NAMES = {
    "1":"Casa",
    "2":"Fora",
    "X":"Empate",
    "Odd":"Ímpar",
    "Even":"Par",
    "12":"Casa/Fora",
    "X2":"Empate/Fora",
    "1X":"Casa/Empate",
    "No Goal":"Sem Gols",
    "X/X":"Empate/Empate",
    "X/2":"Empate/Fora",
    "X/1":"Empate/Casa",
    "1/X":"Casa/Empate",
    "1/1":"Casa/Casa",
    "2/1":"Fora/Casa",
    "2/X":"Fora/Empate",
    "2/2":"Fora/Fora",
    "1/2":"Casa/Fora",
    "All Periods The Same":"O mesmo em ambos",
    "1st Half":"1° Tempo"
}

REAL_MARKET_NAMES = {
    "12":"Casa/Fora",
    "1st Period Winner":"Vencedor 1° Tempo",
    "2nd Period Odd/Even":"2° Tempo Par/Ímpar",
    "Correct Score":"Placar Correto",
    "Correct Score 1st Period":"Placar Correto 2° Tempo",
    "Double Chance":"Dupla Chance",
    "Double Chance Halftime":"Dupla Chance 1° Tempo",
    "First Team To Score":"Primeiro Time a Marcar",
    "HT/FT":"1° Tempo / 2° Tempo",
    "In Which Half Away Team Will Score More Goals?":"Em qual etapa o time de Fora vai fazer mais Gols?",
    "In Which Half Home Team Will Score More Goals?":"Em qual etapa o time de Casa vai fazer mais Gols?",
    "Odd/Even":"Ímpar/Par",
    "Odd/Even Halftime":"Ímpar/Par 1° Tempo",
    "2nd Period Odd/Even":"Ímpar/Par 2°  Tempo",
    "Corners - Under/Exactly/Over":"Escanteios Abaixo/Exatamente/Acima",
    "Total Corners":"Total de Escanteios",
    "Under/Over":"Abaixo/Acima",
    "Under/Over 1st Period":"Abaixo/Acima 1° Tempo",
    "Under/Over Corners - 1st Half":"Abaixo/Acima Escanteios 1° Tempo",
    "Asian Handicap 1st Period":"Asian Handicap 1° Tempo"


}

def process_markets(markets, game_instance):

    for market in markets:
        for cotation in market['Providers'][0]['Bets']:
            Cotation(id=cotation['Id'],
                name=cotation['Name'],
                game=game_instance,
                line=cotation.get('Line',None),
                base_line=cotation.get('BaseLine', None),
                status=cotation['Status'],
                start_price=cotation['StartPrice'],
                price=cotation['Price'],
                settlement=cotation.get('Settlement',None),
                market=Market.objects.get_or_create(pk=market['Id'], defaults={'name':market['Name']})[0],
                last_update=cotation['LastUpdate']
            ).save()

