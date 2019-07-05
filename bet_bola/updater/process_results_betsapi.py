from core.models import Game
from django.utils import timezone
import utils.timezone as tzlocal
import requests
import re
from django.db.models import Max

def process_results():
    print("Updating Scores")
    games = Game.objects.filter(
        score_half='',
        score_full='',
        results_calculated=False,
        start_date__lt=(tzlocal.now() + timezone.timedelta(hours=2, minutes=30))
    )

    games_to_process = []
    for game in games:
        games_to_process.append(str(game.id))

    while games_to_process:
        get_games(games_to_process[:10])
        del games_to_process[:10]
    print("End Updating Scores")


def get_games(games):
    games_ids_string = ','.join(games)

    request = requests.get('https://api.betsapi.com/v1/bet365/result?token=20445-s1B9Vv6E9VSLU1&event_id=' + games_ids_string)
    if request.status_code == 200:
        data_games = request.json()
        if data_games['success'] == 1:
            for index, game_json in enumerate(data_games['results']):
                if not game_json.get('success', True) == 0:
                    update_game_score(game_json, games[index])


def update_game_score(game_json, game_id):
    game = Game.objects.filter(pk=game_id).first()
    game_scores = game_json.get('scores', None)
    
    if game_scores and game:
        print("Updating Game: " + str(game.id))
        score_half = game_scores.get('1')
        score_full = game_scores.get('2')
        
        if score_half and score_full and score_half.get('home') and score_half.get('away') and score_full.get('home') and score_full.get('away'):
            score_half_str = score_half.get('home') + '-' + score_half.get('away')
            score_full_str = score_full.get('home') + '-' + score_full.get('away')

            game.score_half = score_half_str
            game.score_full = score_full_str
            game.save()


def process_games(game_json, game_id):
    games = Game.objects.exclude(
        score_half='',
        score_full='',
        results_calculated=True,
    )
    
    if game and games:
        print("Processing game: " + str(game.id))
        home_1, away_1 = game.score_half.split('-')
        home_2, away_2 = game.score_full.split('-')

        game_scores = {
            '1' : {
                'home': home_1,
                'away': away_1
            },
            '2': {
                'home': home_2
                'away': away_2
            }
        }
        
        process_1X2(game_scores, game.cotations.filter(market__name='1X2'))
        goals_over_under(game_scores, game.cotations.filter(market__name='Gols - Acima/Abaixo'))
        goals_odd_even(game_scores, game.cotations.filter(market__name='Total de Gols Ímpar/Par'))
        home_team_odd_even_goals(game_scores, game.cotations.filter(market__name='Time Casa - Total de Gols Ímpar/Par'))
        away_team_odd_even_goals(game_scores, game.cotations.filter(market__name='Time Fora - Total de Gols Ímpar/Par'))
        half_time_result(game_scores, game.cotations.filter(market__name='Resultado no 1° Tempo'))
        half_time_double_chance(game_scores, game.cotations.filter(market__name='Dupla Chance 1° Tempo'))
        half_time_correct_score(game_scores, game.cotations.filter(market__name='Placar correto 1° Tempo'))
        process_1st_half_goals_odd_even(game_scores, game.cotations.filter(market__name='Ímpar/Par 1° Tempo'))
        home_team_highest_scoring_half(game_scores, game.cotations.filter(market__name='Metade com maior quantidade de Gols - Time Casa'), game.home_team)
        away_team_highest_scoring_half(game_scores, game.cotations.filter(market__name='Metade com maior quantiade de Gols - Time Fora'), game.away_team)
        process_2nd_half_goals_odd_even(game_scores, game.cotations.filter(market__name='Ímpar/Par 2° Tempo'))
        double_chance(game_scores, game.cotations.filter(market__name='Dupla Chance'))
        correct_score(game_scores, game.cotations.filter(market__name='Placar Correto'))
        half_time_full_time(game_scores, game.cotations.filter(market__name='Vencedor 1° Tempo / 2° Tempo'), game.home_team, game.away_team)
        draw_no_bet(game_scores, game.cotations.filter(market__name='Casa/Fora'), game.home_team, game.away_team)
        alternative_total_goals(game_scores, game.cotations.filter(market__name='Total de Gols'))
        result_total_goals(game_scores, game.cotations.filter(market__name='Resultado / Total de Gols'), game.home_team, game.away_team)
        total_goals_both_teams_to_score(game_scores, game.cotations.filter(market__name='Total de Gols / Ambos  Marcam'))
        exact_total_goals(game_scores, game.cotations.filter(market__name='Total de Gols Exato'))
        both_teams_to_score(game_scores, game.cotations.filter(market__name='Ambos Marcam'))
        teams_to_score(game_scores, game.cotations.filter(market__name='Times que Marcam'), game.home_team, game.away_team)
        home_team_exact_goals(game_scores, game.cotations.filter(market__name='Time Casa - Total de Gols Exato'))
        away_team_exact_goals(game_scores, game.cotations.filter(market__name='Time Fora - Total de Gols Exato'))
        half_time_result_both_teams_to_score(game_scores, game.cotations.filter(market__name='Resultado 1° Tempo / Ambos Marcam'), game.home_team, game.away_team)
        half_time_result_total_goals(game_scores, game.cotations.filter(market__name='Resultado 1° Tempo / Total de Gols'), game.home_team, game.away_team)
        both_teams_to_score_in_1st_half(game_scores, game.cotations.filter(market__name='Ambos Marcam 1° Tempo'))
        both_teams_to_score_in_2nd_half(game_scores, game.cotations.filter(market__name='Ambos Marcam 2° Tempo'))
        both_teams_to_score_1st_half_2nd_half(game_scores, game.cotations.filter(market__name='Ambos Marcam 1° e 2° Tempo'))
        first_half_goals(game_scores, game.cotations.filter(market__name='Total de Gols 1° Tempo'))
        exact_1st_half_goals(game_scores, game.cotations.filter(market__name='Total de Gols Exato 1° Tempo'))
        exact_2nd_half_goals(game_scores, game.cotations.filter(market__name='Total de Gols Exato 2° Tempo'))
        to_score_in_half(game_scores, game.cotations.filter(market__name='Haverá Gol'))
        half_with_most_goals(game_scores, game.cotations.filter(market__name='Etapa com mais Gols'))
        process_2nd_half_result(game_scores, game.cotations.filter(market__name='Resultado 2° Tempo'))
        process_2nd_half_goals(game_scores, game.cotations.filter(market__name='Total de Gols - 2° Tempo'))
        result_both_teams_to_score(game_scores, game.cotations.filter(market__name='Resultado / Ambos Marcam'), game.home_team, game.away_team)
        winning_margin(game_scores, game.cotations.filter(market__name='Margem de Vitória'))

        game.cotations.filter(market__name='Especiais').update(settlement=1)
        win_without_taking_goals(game_scores, game.cotations.filter(market__name='Especiais'))
        win_whatever_half(game_scores, game.cotations.filter(market__name='Especiais'))
        win_both_halves(game_scores, game.cotations.filter(market__name='Especiais'))
        mark_both_halves(game_scores, game.cotations.filter(market__name='Especiais'))

        game.results_calculated = True
        game.save()


def process_1X2(scores, cotations):
    if scores.get('2', None):
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
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        total_goals = home + away

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            cotations.filter(name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def goals_odd_even(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        total_goals = home + away

        even = (total_goals % 2) == 0

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if even:
                cotations.filter(name='Par').update(settlement=2)
            else:
                cotations.filter(name='Ímpar').update(settlement=2)



def home_team_odd_even_goals(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])

        even = (home % 2) == 0

        if cotations.count() > 0:
            cotations.update(settlement=1)
            if even:
                cotations.filter(name__contains='Par').update(settlement=2)
            else:
                cotations.filter(name__contains='Ímpar').update(settlement=2)



def away_team_odd_even_goals(scores, cotations):
    if scores.get('2', None):
        away = int(scores['2']['away'])

        even = (away % 2) == 0

        if cotations.count() > 0:
            cotations.update(settlement=1)
            if even:
                cotations.filter(name__contains='Par').update(settlement=2)
            else:
                cotations.filter(name__contains='Ímpar').update(settlement=2)


def half_time_result(scores, cotations):
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])

        if cotations.count() > 0:
            cotations.update(settlement=1)
            if home > away:
                cotations.filter(name='Casa').update(settlement=2)
            elif home < away:
                cotations.filter(name='Fora').update(settlement=2)
            else:
                cotations.filter(name='Empate').update(settlement=2)


def half_time_double_chance(scores, cotations):
    if scores.get('1', None):
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
    if scores.get('1', None):
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
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])
        total_goals = home + away

        even = (total_goals % 2) == 0

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if even:
                cotations.filter(name='Par').update(settlement=2)
            else:
                cotations.filter(name='Ímpar').update(settlement=2)


def home_team_highest_scoring_half(scores, cotations, home_name):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        home_2 = int(scores['2']['home']) - home_1

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
    if scores.get('1', None) and scores.get('2', None):
        away_1 = int(scores['1']['away'])
        away_2 = int(scores['2']['away']) - away_1

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
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])
        
        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        total_goals = home_2 + away_2

        even = (total_goals % 2) == 0

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if even:
                cotations.filter(name='Par').update(settlement=2)
            else:
                cotations.filter(name='Ímpar').update(settlement=2)


def double_chance(scores, cotations):
    if scores.get('2', None):
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
    if scores.get('2', None):
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
    if scores.get('1', None) and scores.get('2', None):
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
            elif home_1 > away_1  and home_2 == away_2:
                cotations.filter(name__istartswith=home_name, name__iendswith='Empate').update(settlement=2)

            if home_1 < away_1 and home_2 > away_2:
                cotations.filter(name__istartswith=away_name, name__iendswith=home_name).update(settlement=2)
            elif home_1 < away_1 and home_2 < away_2:
                cotations.filter(name__istartswith=away_name, name__iendswith=away_name).update(settlement=2)
            elif home_1 < away_1  and home_2 == away_2:
                cotations.filter(name__istartswith=away_name, name__iendswith='Empate').update(settlement=2)

            if home_1 == away_1 and home_2 > away_2:
                cotations.filter(name__istartswith='Empate', name__iendswith=home_name).update(settlement=2)
            elif home_1 == away_1 and home_2 < away_2:
                cotations.filter(name__istartswith='Empate', name__iendswith=away_name).update(settlement=2)
            elif home_1 == away_1  and home_2 == away_2:
                cotations.filter(name__istartswith='Empate', name__iendswith='Empate').update(settlement=2)


def draw_no_bet(scores, cotations, home_name, away_name):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if home > away:
                cotations.filter(name__icontains=home_name).update(settlement=2)
            elif home < away:
                cotations.filter(name__icontains=away_name).update(settlement=2)


def alternative_total_goals(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        total_goals = home + away

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            cotations.filter(name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def result_total_goals(scores, cotations, home_name, away_name):
    if scores.get('2', None):
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



def total_goals_both_teams_to_score(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        total_goals = home + away
        both_mark = bool(home and away)

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            if both_mark:
                cotations.filter(name__iendswith='Sim', name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
                cotations.filter(name__iendswith='Sim', name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)
            else:
                cotations.filter(name__iendswith='Não', name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
                cotations.filter(name__iendswith='Não', name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def exact_total_goals(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        total_goals = home + away

        if cotations.count() > 0:
            cotations.update(settlement=1)

            cotations.filter(name__contains=str(int(total_goals))).update(settlement=2)

            latest_total_goals = cotations.aggregate(max_value=Max('total_goals'))['max_value']
            if latest_total_goals:
                if total_goals > latest_total_goals:
                    cotations.filter(name__contains=int(latest_total_goals)).update(settlement=2)

        
def both_teams_to_score(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        both_mark = bool(home and away)

        if cotations.count() > 0:
            cotations.update(settlement=1)
            if both_mark:
                cotations.filter(name='Sim').update(settlement=2)
            else:
                cotations.filter(name='Não').update(settlement=2)


def teams_to_score(scores, cotations, home_name, away_name):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])


        if cotations.count() > 0:
            cotations.update(settlement=1)

            if home > 0 and away == 0:
                cotations.filter(name__icontains=home_name, name__contains='Apenas').update(settlement=2)
            elif away > 0 and home == 0:
                cotations.filter(name__icontains=away_name, name__contains='Apenas').update(settlement=2)
            elif home > 0 and away > 0:
                cotations.filter(name='Ambos os Times').update(settlement=2)
            elif home == 0 and away == 0:
                cotations.filter(name='Sem Gols').update(settlement=2)


def home_team_exact_goals(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])

        if cotations.count() > 0:
            cotations.update(settlement=1)

            cotations.filter(name__contains=str(int(home))).update(settlement=2)
            latest_total_goals = cotations.aggregate(max_value=Max('total_goals'))['max_value']
            if home > latest_total_goals:
                cotations.filter(name__contains=int(latest_total_goals)).update(settlement=2)


def away_team_exact_goals(scores, cotations):
    if scores.get('2', None):
        away = int(scores['2']['away'])

        if cotations.count() > 0:
            cotations.update(settlement=1)

            cotations.filter(name__contains=str(int(away))).update(settlement=2)
            latest_total_goals = cotations.aggregate(max_value=Max('total_goals'))['max_value']
            if away > latest_total_goals:
                cotations.filter(name__contains=int(latest_total_goals)).update(settlement=2)


def half_time_result_both_teams_to_score(scores, cotations, home_name, away_name):
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])
        both_mark = bool(home and away)

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            if home > away and both_mark:
                cotations.filter(name__istartswith=home_name, name__contains='Sim').update(settlement=2)
            elif home > away and not both_mark:
                cotations.filter(name__istartswith=home_name, name__contains='Não').update(settlement=2)

            if home < away and both_mark:
                cotations.filter(name__istartswith=away_name, name__contains='Sim').update(settlement=2)
            elif home < away and not both_mark:
                cotations.filter(name__istartswith=away_name, name__contains='Não').update(settlement=2)
            
            if home == away and both_mark:
                cotations.filter(name__istartswith='Empate', name__contains='Sim').update(settlement=2)
            elif home == away and not both_mark:
                cotations.filter(name__istartswith='Empate', name__contains='Não').update(settlement=2)


def half_time_result_total_goals(scores, cotations, home_name, away_name):
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])
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


def both_teams_to_score_in_1st_half(scores, cotations):
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])
        both_mark = bool(home and away)

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if both_mark:
                cotations.filter(name__contains='Sim').update(settlement=2)
            else:
                cotations.filter(name__contains='Não').update(settlement=2)


def both_teams_to_score_in_2nd_half(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        both_mark = bool(home_2 and away_2)

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if both_mark:
                cotations.filter(name__contains='Sim').update(settlement=2)
            else:
                cotations.filter(name__contains='Não').update(settlement=2)


def both_teams_to_score_1st_half_2nd_half(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        both_mark_1 = bool(home_1 and away_1)

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        both_mark_2 = bool(home_2 and away_2)

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if both_mark_1:
                if both_mark_2:
                    cotations.filter(name__istartswith='Sim', name__iendswith='Sim').update(settlement=2)
                else:
                    cotations.filter(name__istartswith='Sim', name__iendswith='Não').update(settlement=2)
            else:
                if both_mark_2:
                    cotations.filter(name__istartswith='Não', name__iendswith='Sim').update(settlement=2)
                else:
                    cotations.filter(name__istartswith='Não', name__iendswith='Não').update(settlement=2)


def process_2nd_half_goals(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):

        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        total_goals = home_2 + away_2

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            cotations.filter(name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def first_half_goals(scores, cotations):
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])
        total_goals = home + away

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            cotations.filter(name__contains='Acima', total_goals__lt=total_goals).update(settlement=2)
            cotations.filter(name__contains='Abaixo', total_goals__gt=total_goals).update(settlement=2)


def exact_1st_half_goals(scores, cotations):
    if scores.get('1', None):
        home = int(scores['1']['home'])
        away = int(scores['1']['away'])
        total_goals = home + away

        if cotations.count() > 0:
            cotations.update(settlement=1)

            cotations.filter(name__contains=str(int(total_goals))).update(settlement=2)

            latest_total_goals = cotations.aggregate(max_value=Max('total_goals'))['max_value']
            if latest_total_goals:
                if total_goals > latest_total_goals:
                    cotations.filter(name__contains=int(latest_total_goals)).update(settlement=2)


def exact_2nd_half_goals(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        total_goals = home_2 + away_2

        if cotations.count() > 0:
            cotations.update(settlement=1)

            cotations.filter(name__contains=str(int(total_goals))).update(settlement=2)

            latest_total_goals = cotations.aggregate(max_value=Max('total_goals'))['max_value']
            if latest_total_goals:
                if total_goals > latest_total_goals:
                    cotations.filter(name__contains=int(latest_total_goals)).update(settlement=2)


def to_score_in_half(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if home_1 > 0 or away_1 > 0:
                cotations.filter(name__contains='1° Tempo', name__startswith='Sim').update(settlement=2)
            if home_2 > 0 or away_2 > 0:
                cotations.filter(name__contains='2° Tempo', name__startswith='Sim').update(settlement=2)


def half_with_most_goals(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])
        total_1 = home_1 + away_1

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1
        total_2 = home_2 + away_2

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if total_1 > total_2:
                cotations.filter(name='1° Tempo').update(settlement=2)
            elif total_2 < total_2:
                cotations.filter(name='2° Tempo').update(settlement=2)
            else:
                cotations.filter(name='Igual').update(settlement=2)


def process_2nd_half_result(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if home_2 > away_2:
                cotations.filter(name='Casa').update(settlement=2)
            elif home_2 < away_2:
                cotations.filter(name='Fora').update(settlement=2)
            else:
                cotations.filter(name='Empate').update(settlement=2)
            



def result_both_teams_to_score(scores, cotations, home_name, away_name):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        both_mark = bool(home and away)

        if cotations.count() > 0:
            cotations.update(settlement=1)
            
            if home > away and both_mark:
                cotations.filter(name__contains=home_name, name__startswith='Sim').update(settlement=2)
            elif home > away and not both_mark:
                cotations.filter(name__contains=home_name, name__startswith='Não').update(settlement=2)

            if home < away and both_mark:
                cotations.filter(name__contains=away_name, name__startswith='Sim').update(settlement=2)
            elif home < away and not both_mark:
                cotations.filter(name__contains=away_name, name__startswith='Não').update(settlement=2)
            
            if home == away and both_mark:
                cotations.filter(name__contains='Empate', name__startswith='Sim').update(settlement=2)
            elif home == away and not both_mark:
                cotations.filter(name__contains='Empate', name__startswith='Não').update(settlement=2)


def winning_margin(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])
        total_goals = home + away
        has_goals = bool(home and away)
        goals_difference = home - away

        if cotations.count() > 0:
            cotations.update(settlement=1)

            if goals_difference > 0:
                cotations.filter(name__startswith='Casa', name__contains=abs(goals_difference)).update(settlement=2)
            elif goals_difference < 0:
                cotations.filter(name__startswith='Fora', name__contains=abs(goals_difference)).update(settlement=2)
            elif goals_difference == 0:
                cotations.filter(name__contains='Empate').update(settlement=2)
            elif not has_goals:
                cotations.filter(name__contains='Nenhum Gol').update(settlement=2)

            latest_total_goals = cotations.aggregate(max_value=Max('total_goals'))['max_value']
            if latest_total_goals:
                if total_goals > latest_total_goals:
                    if goals_difference > 0:
                        cotations.filter(name__startswith='Casa', name__contains=int(latest_total_goals)).update(settlement=2)
                    elif goals_difference < 0:
                        cotations.filter(name__startswith='Fora', name__contains=int(latest_total_goals)).update(settlement=2)



def win_without_taking_goals(scores, cotations):
    if scores.get('2', None):
        home = int(scores['2']['home'])
        away = int(scores['2']['away'])

        if cotations.count() > 0:

            if home > away and away == 0:
                cotations.filter(name='Casa - Ganhar sem tomar Gol').update(settlement=2)
            
            if home < away and home == 0:
                cotations.filter(name='Fora - Ganhar sem tomar Gol').update(settlement=2)


def win_whatever_half(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        if cotations.count() > 0:

            if home_1 > away_1 or home_2 > away_2:
                cotations.filter(name='Casa - Ganhar Qualquer Etapa').update(settlement=2)
            
            if home_1 < away_1 or home_2 < away_2:
                cotations.filter(name='Fora - Ganhar Qualquer Etapa').update(settlement=2)


def win_both_halves(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        if cotations.count() > 0:
            
            if home_1 > away_1 and home_2 > away_2:
                cotations.filter(name='Casa - Ganhar Ambas Etapas').update(settlement=2)
            
            if home_1 < away_1 and home_2 < away_2:
                cotations.filter(name='Fora - Ganhar Ambas Etapas').update(settlement=2)


def mark_both_halves(scores, cotations):
    if scores.get('1', None) and scores.get('2', None):
        home_1 = int(scores['1']['home'])
        away_1 = int(scores['1']['away'])

        home_2 = int(scores['2']['home']) - home_1
        away_2 = int(scores['2']['away']) - away_1

        if cotations.count() > 0:
            if home_1 > 0 and home_2 > 0:
                cotations.filter(name='Casa - Marcar em Ambas Etapas').update(settlement=2)
            
            if away_1 > 0 and away_2 > 0:
                cotations.filter(name='Fora - Marcar em Ambas Etapas').update(settlement=2)


