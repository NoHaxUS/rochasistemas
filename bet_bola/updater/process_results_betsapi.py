from core.models import Game
from django.utils import timezone
from utils.timezone import  tzlocal
import requests


def process_results():

    games = Game.objects.filter(results_calculated=False, 
        start_date__lt=(tzlocal.now() + timezone.timedelta(hours=3))
    )

    games_to_process = []
    for game in games:
        games.append(game.id)
        if len(games_to_process) >= 10:
            get_games(games_to_process)
            games_to_process.clear()


def get_games(games):
    game_ids_string = games.join(',')

    request = requests.get('https://api.betsapi.com/v1/bet365/result?token=20445-s1B9Vv6E9VSLU1&event_id=' + games_ids_string)
    if request.status_code == 200:
        data_games = request.json()
        if data_games['success'] == 1:
            for game_json in data_games['results']:
                process_games(game_json)


def process_games(game_json):
    game = Game.objects.filter(pk=game_json['id']).first()
    game_scores = game_json.get('scores', None):
    if game_scores and game:
        process_1X2(game_scores, game.cotations.filter(market__name='1X2'))




def process_1X2(scores, cotations):
    



