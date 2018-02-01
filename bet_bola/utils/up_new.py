import requests
from core.models import *
from user.models import GeneralConfigurations
import utils.timezone as tzlocal
from django.db.models import Count
from django.db.models import Q

MARKET_NAME = {
    "Team To Score First": "Time a Marcar Primeiro",
    "Result/Total Goals": "Resultado/Total de Gol(s)",
    "Correct Score 1st Half": "Resultado Exato no Primeiro Tempo",
    "Both Teams To Score": "2 Times Marcam",
    "3Way Result 1st Half": "Vencedor Primeiro Tempo",
    "Total - Away": "Total de Gols do Visitante",
    "Double Chance": "Dupla Chance",
    "Total - Home": "Total de Gols da Casa",
    "Over/Under 1st Half": "Total de Gols do Primeiro Tempo, Acima/Abaixo",
    "Win To Nil": "Vencedor Não tomará Gol(s)",
    "Correct Score": "Resultado Exato",
    "3Way Result": "Vencedor do Encontro",
    "Away Team Score a Goal": "Visitante Marca pelo menos Um Gol(s)",
    "Home/Away": "Casa/Visitante",
    "Over/Under": "Total de Gol(s) no Encontro, Acima/Abaixo",
    "Highest Scoring Half": "Etapa com Mais Gol(s)",
    "Clean Sheet - Home": "Time da Casa Não Tomará Gol(s)",
    "Clean Sheet - Away": "Time Visitante Não Tomará Gol(s)",
    "HT/FT Double": "Intervalo/Final de Jogo",
    "Results/Both Teams To Score": "Resultado/2 Times Marcam",
    "Home Team Score a Goal": "Time da casa Marca",
    "Win Both Halves": "Vencedor nas Duas Etapas",
    "Exact Goals Number": "Número Exato de Gol(s)",
    "Odd/Even": "Ímpar/Par",
}


def renaming_cotations(string, total):

    COTATION_NAME = {
        "Under": "Abaixo",
        "Over": "Acima",
        "Draw": "Empate",
        "Away": "Visitante",
        "Home": "Casa",
        "1st Half": "1° Tempo",
        "2nd Half": "2° Tempo",
        "No": "Não",
        "Yes": "Sim",
        "More": "Mais de"
    }

    for i in COTATION_NAME.keys():
        if i in string:
            string = string.replace(i, COTATION_NAME[i])
            string = string + " " + total
    return string


TOKEN = 'DLHVB3IPJuKN8dxfV5ju0ajHqxMl4zx91u5zxOwLS8rHd5w6SjJeLEOaHpR5'


def consuming_championship_api():

    print('Atualizando Campeonatos')
    request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
                           TOKEN + "&include=country&tz=America/Santarem")
    check_request_status(request)
    total_pages = request.json().get('meta')['pagination']['total_pages']
    process_json_championship(request.json())

    for actual_page in range(1, total_pages):
        request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
                               TOKEN + "&include=country&tz=America/Santarem&page=" + str(actual_page + 1))

    consuming_game_cotation_api()


def process_json_championship(json_response):

    championship_array = json_response.get('data')

    if championship_array:
        for championship in championship_array:
            Championship(pk=championship['id'], name=championship['name'],
                         country=championship['country']['data']['name']).save()
    else:
        print("O array de campeonatos retornou vazio.")


def process_json_games_cotations(json_response):
    
    if GeneralConfigurations.objects.filter(pk=1):
        max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
    else:
        max_cotation_value = 200

    games_array = json_response.get('data')
    for game in games_array:
        Game(pk=game['id'],
             name=game['localTeam']['data']['name'] +
             " x " + game['visitorTeam']['data']['name'],
             status_game=game['time']['status'],
             local_team_score=game['scores']['localteam_score'],
             visitor_team_score=game['scores']['visitorteam_score'],
             ht_score=game['scores']['ht_score'],
             ft_score=game['scores']['ft_score'],
             odds_calculated=game['winning_odds_calculated'],
             start_game_date=datetime.strptime(
            game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
            championship=Championship.objects.get(pk=game["league_id"])).save()
        save_odds(game['id'], game['odds'], max_cotation_value)


def check_request_status(request):
    if not request.status_code == 200:
        print('Falha: Url:' + request.url)
        print('Status: ' + request.status_code)


def consuming_game_cotation_api():

    first_date = str(tzlocal.now().year) + "-" + \
        str(tzlocal.now().month) + "-" + str((tzlocal.now().day) - 1)
    second_date = str(tzlocal.now().year) + "-" + \
        str(tzlocal.now().month) + "-" + str((tzlocal.now().day + 8))

    print("Atualizando os Games")

    request = requests.get(
        'https://soccer.sportmonks.com/api/v2.0/fixtures/between/' + first_date + '/' + second_date + '?api_token=' + TOKEN + '&include=localTeam,visitorTeam,odds&tz=America/Santarem')
    total_pages = request.json().get('meta')['pagination']['total_pages']
    check_request_status(request)
    process_json_games_cotations(request.json())

    for actual_page in range(1, total_pages):
        next = 'https://soccer.sportmonks.com/api/v2.0/fixtures/between/' + first_date + '/' + second_date + '?page=' + \
            str(actual_page + 1) + '&api_token=' + TOKEN + \
            '&include=localTeam,visitorTeam,odds&tz=America/Santarem'
        request = requests.get(next)
        process_json_games_cotations(request.json())


def get_bet365_from_bookmakers(bookmakers):

    for bookmaker in bookmakers:
        if bookmaker['id'] == 2:
            return bookmaker
    return bookmakers[0]


def save_odds(game_id, odds, max_cotation_value):

    
    odds_array = odds.get('data')
    game_instance = Game.objects.get(pk=game_id)

    for market in odds_array:
        kind_name = market['name']
        if kind_name in MARKET_NAME.keys():
            print('Market in: '+ kind_name)
            bookmakers = market['bookmaker']['data']
            bookmaker = get_bet365_from_bookmakers(bookmakers)
            print(bookmaker)
            cotations = bookmaker['odds']['data']

            for cotation in cotations:

                if kind_name == '3Way Result' and cotation['label'] in ['1', '2', 'X']:
                    cotation_value = max_cotation_value if float(
                        cotation['value']) > max_cotation_value else float(cotation['value'])
                    Cotation(name=renaming_cotations(cotation['label'], " " if cotation['total'] == None else cotation['total']).strip(),
                             value=cotation_value,
                             original_value=cotation_value,
                             game=game_instance,
                             is_standard=True,
                             handicap=cotation['handicap'],
                             total=cotation['total'],
                             winning=cotation['winning'],
                             kind=MARKET_NAME.setdefault(kind_name, kind_name)).save()

                elif kind_name == 'Result/Total Goals':
                    cotation_value = max_cotation_value if float(
                        cotation['value']) > max_cotation_value else float(cotation['value'])
                    Cotation(name=renaming_cotations(cotation['label'], " ").strip(),
                             value=cotation_value,
                             original_value=cotation_value,
                             game=game_instance,
                             is_standard=False,
                             handicap=cotation['handicap'],
                             total=cotation['total'],
                             winning=cotation['winning'],
                             kind=MARKET_NAME.setdefault(kind_name, kind_name)).save()
                else:
                    cotation_value = max_cotation_value if float(
                        cotation['value']) > max_cotation_value else float(cotation['value'])
                        
                    Cotation(name=renaming_cotations(cotation['label'], " " if cotation['total'] == None else cotation['total']).strip(),
                             value=cotation_value,
                             original_value=cotation_value,
                             game=game_instance,
                             is_standard=False,
                             handicap=cotation['handicap'],
                             total=cotation['total'],
                             winning=cotation['winning'],
                             kind=MARKET_NAME.setdefault(kind_name, kind_name)).save()


def processing_cotations_v2():

    games_to_process = Game.objects.annotate(cotations_count=Count('cotations')).filter(
        odds_calculated=True, status_game="FT", odds_processed=False, ft_score__isnull=False, cotations_count__gt=0)

    for game in games_to_process:
        not_calculaded_cotations = game.cotations.filter(winning__isnull=True)
        vencedor_encontro(game, not_calculaded_cotations)



def vencedor_encontro(game, all_cotations):

    cotations = all_cotations.filter(kind='Vencedor do Encontro')
    if cotations.count() > 0:
        c1 = cotations.filter('1')
        c2 = cotations.filter('2')
        cX = cotations.filter('X')

        if game.local_team_score > game.visitor_team_score:
            c1.update(winning=True)
            c2.update(winning=False)
            cX.update(winning=False)
        elif game.local_team_score < game.visitor_team_score:
            c1.update(winning=False)
            c2.update(winning=True)
            cX.update(winning=False)
        else:
            c1.update(winning=False)
            c2.update(winning=False)
            cX.update(winning=True)

def casa_visitante(game, all_cotations):

    cotations = all_cotations.filter(kind='Casa/Visitante')
    if cotations.count() > 0:
        c1 = cotations.filter('1')
        c2 = cotations.filter('2')

    if game.local_team_score > game.visitor_team_score:
        c1.update(winning=True)
        c2.update(winning=False)
    
    elif game.local_team_score < game.visitor_team_score:
        c1.update(winning=False)
        c2.update(winning=True)
    else:
        c1.update(winning=False)
        c2.update(winning=False)

"""
def dupla_chance(game, all_cotations):

    cotations = all_cotations.filter(kind='Dupla Chance')
    if cotations.count() > 0:
        c1X = cotations.filter('1')
        c2X = cotations.filter('2')
        c12 = cotations.filter('2')
        c_casa_empate = cotations.filter('2')
        c_casa_visitante = cotations.filter('2')
        c_empate_visitante = cotations.filter('2')

"""


