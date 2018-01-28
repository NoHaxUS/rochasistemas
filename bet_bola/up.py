import os
import sys
import django

from core.models import Championship,Game,Cotation,BetTicket
from datetime import datetime
from django.utils import timezone
from core.models import *
from user.models import GeneralConfigurations
import requests

sys.path.append('C:\\DEV\\bet_bola2\\bet_bola')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
consuming_championship_api()

TOKEN = 'DLHVB3IPJuKN8dxfV5ju0ajHqxMl4zx91u5zxOwLS8rHd5w6SjJeLEOaHpR5'


def consuming_championship_api():
    
    request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token="+TOKEN+"&include=country&tz=America/Santarem")
    
    if not request.status_code == 200:
        print('Falha ao buscar campeonatos')
        print(request.status_code)
        return None

    print("Atualizando Campeonatos")
    json_response = request.json()
    championship_array = json_response.get('data')
    championship_bulk = list()

    if championship_array:
        for championship in championship_array:
            c = Championship(pk=championship['id'],name = championship['name'], country = championship['country']['data']['name'])
            championship_bulk.append(c)
    else:
        print("O array de campeonatos retornou vazio.")

    Championship.objects.bulk_create(championship_bulk)
    
"""
def consuming_game_cotation_api(request):
    request = requests.get('https://soccer.sportmonks.com/api/v2.0/fixtures/between/2018-01-27/2018-01-28?api_token=DLHVB3IPJuKN8dxfV5ju0ajHqxMl4zx91u5zxOwLS8rHd5w6SjJeLEOaHpR5&include=localTeam,visitorTeam,odds&tz=America/Santarem')
    if not request.status_code == 200:
        print('Falha ao atualizar Jogos')
        print(request.status_code)



    json_response = request.json()
    games_array = json_response.get('data')

    for game in games_array:
        Game(pk=game['id'],
         )



"""