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
        goals_over_under(game_scores, game.cotations.filter(market__name='Gols - Acima/Abaixo'))
        goals_odd_even(game_scores, game.cotations.filter(market__name='Total de Gols Ímpar/Par'))
        home_team_odd_even_goals(game_scores, game.cotations.filter(market__name='Time Casa - Total de Gols Ímpar/Par'))
        away_team_odd_even_goals(game_scores, game.cotations.filter(market__name='Time Fora - Total de Gols Ímpar/Par'))




def process_1X2(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])

    if cotations.count() > 0:
        cotations.update(settlement=1)
        if home > away:
            cotations.filter(name='Casa').update(settlement=2)
        elif home < away:
            cotations.filter(name='Fora').update(settlement=2)
        else:
            cotations.filter(name='Empate').update(settlement=2)



def goals_over_under(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])
    total_goals = home + away

    if cotations.count() > 0:
        cotations.update(settlement=1)
        
        cotations.filter(name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
        cotations.filter(name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def goals_odd_even(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])
    total_goals = home + away

    even = (total_gols % 2) == 0

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if even:
            cotations.filter(name='Par').update(settlement=2)
        else:
            cotations.filter(name='Ímpar').update(settlement=2)



def home_team_odd_even_goals(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])

    even = (home % 2) == 0

    if cotations.count() > 0:
        cotations.update(settlement=1)
        if even:
            cotations.filter(name__contains='Par').update(settlement=2)
        else:
            cotations.filter(name__contains='Ímpar').update(settlement=2)



def away_team_odd_even_goals(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])

    even = (away % 2) == 0

    if cotations.count() > 0:
        cotations.update(settlement=1)
        if even:
            cotations.filter(name__contains='Par').update(settlement=2)
        else:
            cotations.filter(name__contains='Ímpar').update(settlement=2)


def half_time_result(scores, cotations):
    home = int(scores['1']['home'])
    away = int(scores['1']['away'])

    if cotations.count() > 0:
        cotations.update(settlement=1)
        if home > away
            cotations.filter(name='Casa').update(settlement=2)
        elif home < away:
            cotations.filter(name='Fora').update(settlement=2)
        else:
            cotations.filter(name='Empate').update(settlement=2)


def half_time_double_chance(scores, cotations):
    home = int(scores['1']['home'])
    away = int(scores['1']['away'])

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if home > away:
            cotations.filter(name__contains='Casa').update(settlement=2)
        elif home < away:
            cotations.filter(name__contains='Fora').update(settlement=2)
        else:
            cotations.filter(name__contains='Empate').update(settlement=2)


def half_time_correct_score(scores, cotations):
    home = int(scores['1']['home'])
    away = int(scores['1']['away'])

    correct_score_string = (str(home) + '-' + str(away)).strip()

    if cotations.count() > 0:
        cotations.update(settlement=1)
        if home > away:
            cotations.filter(name__contains='Casa').filter(name__contains=correct_score_string).update(settlement=2)
        elif home < away:
            cotations.filter(name__contains='Fora').filter(name__contains=correct_score_string).update(settlement=2)
        else:
            cotations.filter(name__contains='Empate').filter(name__contains=correct_score_string).update(settlement=2)


def process_1st_half_goals_odd_even(scores, cotations):
    home = int(scores['1']['home'])
    away = int(scores['1']['away'])
    total_goals = home + away

    even = (total_gols % 2) == 0

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if even:
            cotations.filter(name='Par').update(settlement=2)
        else:
            cotations.filter(name='Ímpar').update(settlement=2)


def home_team_highest_scoring_half(scores, cotations, home_name):
    home_1 = int(scores['1']['home'])
    home_2 = int(scores['2']['home'])

    home_balance = home_1 - home_2

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if home_balance > 0:
            cotations.filter(name__icontains=home_name).filter(name__contains='1° Tempo').update(settlement=2)
        elif home_balance < 0:
            cotations.filter(name__icontains=home_name).filter(name__contains='2° Tempo').update(settlement=2)
        else:
            cotations.filter(name__icontains=home_name).filter(name__contains='Igual').update(settlement=2)


def away_team_highest_scoring_half(scores, cotations, away_name):
    away_1 = int(scores['1']['away'])
    away_2 = int(scores['2']['away'])

    away_balance = away_1 - away_2

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if away_balance > 0:
            cotations.filter(name__icontains=away_name).filter(name__contains='1° Tempo').update(settlement=2)
        elif away_balance < 0:
            cotations.filter(name__icontains=away_name).filter(name__contains='2° Tempo').update(settlement=2)
        else:
            cotations.filter(name__icontains=away_name).filter(name__contains='Igual').update(settlement=2)


def process_2nd_half_goals_odd_even(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])
    total_goals = home + away

    even = (total_gols % 2) == 0

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if even:
            cotations.filter(name='Par').update(settlement=2)
        else:
            cotations.filter(name='Ímpar').update(settlement=2)


def double_chance(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if home > away:
            cotations.filter(name__contains='Casa').update(settlement=2)
        elif home < away:
            cotations.filter(name__contains='Fora').update(settlement=2)
        else:
            cotations.filter(name__contains='Empate').update(settlement=2)


def correct_score(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])

    correct_score_string = (str(home) + '-' + str(away)).strip()

    if cotations.count() > 0:
        cotations.update(settlement=1)
        if home > away:
            cotations.filter(name__contains='Casa').filter(name__contains=correct_score_string).update(settlement=2)
        elif home < away:
            cotations.filter(name__contains='Fora').filter(name__contains=correct_score_string).update(settlement=2)
        else:
            cotations.filter(name__contains='Empate').filter(name__contains=correct_score_string).update(settlement=2)



def half_time_full_time(scores, cotations, home_name, away_name):
    home_1 = int(scores['1']['home'])
    away_1 = int(scores['1']['away'])

    home_2 = int(scores['2']['home']) - home_1
    away_2 = int(scores['2']['away']) - away_1

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if home_1 > away_1 and home_2 > away_2:
            cotations.filter(name__istartswith=home_name, name__iendswith=home_name).update(settlement=2)
        elif home_1 > away_1 and home_2 < away_2:
            cotations.filter(name__istartswith=home_name, name__iendswith=away_name).update(settlement=2)
        elif home_1 > away_2  and home_2 == away_2:
            cotations.filter(name__istartswith=home_name, name__iendswith='Empate').update(settlement=2)

        if home_1 < away_1 and home_2 > away_2:
            cotations.filter(name__istartswith=away_name, name__iendswith=home_name).update(settlement=2)
        elif home_1 < away_1 and home_2 < away_2:
            cotations.filter(name__istartswith=away_name, name__iendswith=away_name).update(settlement=2)
        elif home_1 < away_2  and home_2 == away_2:
            cotations.filter(name__istartswith=away_name, name__iendswith='Empate').update(settlement=2)

        if home_1 == away_1 and home_2 > away_2:
            cotations.filter(name__istartswith='Empate', name__iendswith=home_name).update(settlement=2)
        elif home_1 == away_1 and home_2 < away_2:
            cotations.filter(name__istartswith='Empate', name__iendswith=away_name).update(settlement=2)
        elif home_1 == away_2  and home_2 == away_2:
            cotations.filter(name__istartswith='Empate', name__iendswith='Empate').update(settlement=2)


def draw_no_bet(scores, cotations, away_name, home_name):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])

    if cotations.count() > 0:
        cotations.update(settlement=1)

        if home > away:
            cotations.filter(name__icontains=home_name).update(settlement=2)
        elif home < away:
            cotations.filter(name__icontains=away_name).update(settlement=2)


def alternative_total_goals(scores, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])
    total_goals = home + away

    if cotations.count() > 0:
        cotations.update(settlement=1)
        
        cotations.filter(name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
        cotations.filter(name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def result_total_goals(scores, cotations, home_name, away_name):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])
    total_goals = home + away

    if cotations.count() > 0:
        cotations.update(settlement=1)
        
        if home > away:
            cotations.filter(name__istartswith=home_name, name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__istartswith=home_name, name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)
        elif home < away:
            cotations.filter(name__istartswith=away_name, name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__istartswith=away_name, name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)
        elif home == away:
            cotations.filter(name__istartswith='Empate', name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__istartswith='Empate', name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)



def total_goals_both_teams_to_score(score, cotations):
    home = int(scores['2']['home'])
    away = int(scores['2']['away'])
    total_goals = home + away
    both_mark = home and away

    if cotations.count() > 0:
        cotations.update(settlement=1)
        
        if both_mark:
            cotations.filter(name__iendswith='Sim', name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__iendswith='Sim', name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)
        else:
            cotations.filter(name__iendswith='Não', name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__iendswith='Não', name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)
