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
        games.append(game)
        if len(games_to_process) >= 10:
            process_games(games_to_process)
            games_to_process.clear()


def process_games(games):

    game_ids = [game.id for game in games]
    game_ids_string = games_ids.join(',')

    request = requests.get('https://api.betsapi.com/v1/bet365/result?token=20445-s1B9Vv6E9VSLU1&event_id=' + games_ids_string)
