import requests
from core.models import Game, Cotation, Championship, BetTicket
from user.models import GeneralConfigurations
import utils.timezone as tzlocal
import datetime
from django.db.models import Count
from django.db.models import F



MARKET_NAME = {
    "Result/Total Goals": "Resultado/Total de Gol(s)",
    "Correct Score 1st Half": "Resultado Exato no Primeiro Tempo",
    "Both Teams To Score": "2 Times Marcam",
    "3Way Result 1st Half": "Vencedor do Primeiro Tempo",
    "Total - Away": "Total de Gols do Visitante",
    "Double Chance": "Dupla Chance",
    "Total - Home": "Total de Gols da Casa",
    "Over/Under 1st Half": "Total de Gols do Primeiro Tempo, Acima/Abaixo",
    "Win To Nil": "Vencer e não tomar Gol(s)",
    "Correct Score": "Resultado Exato",
    "3Way Result": "Vencedor do Encontro",
    "Away Team Score a Goal": "Visitante Marca pelo menos Um Gol(s)",
    "Home/Away": "Casa/Visitante",
    "Over/Under": "Total de Gol(s) no Encontro, Acima/Abaixo",
    "Highest Scoring Half": "Etapa com Mais Gol(s)",
    "Clean Sheet - Home": "Time da Casa NÃO Tomará Gol(s)",
    "Clean Sheet - Away": "Time Visitante NÃO Tomará Gol(s)",
    "Results/Both Teams To Score": "Resultado/2 Times Marcam",
    "Home Team Score a Goal": "Time da Casa Marca",
    "Win Both Halves": "Vencedor nas Duas Etapas",
    "Exact Goals Number": "Número Exato de Gol(s)",
    "Odd/Even": "Placar Impar/Par",
}


MARKET_NAME_SMALL_TEAMS = {

    "Result/Total Goals": "Resultado/Total de Gol(s)",
    "Both Teams To Score": "2 Times Marcam",
    "Total - Away": "Total de Gols do Visitante",
    "Double Chance": "Dupla Chance",
    "Total - Home": "Total de Gols da Casa",
    "Win To Nil": "Vencer e não tomar Gol(s)",
    "Correct Score": "Resultado Exato",
    "3Way Result": "Vencedor do Encontro",
    "Away Team Score a Goal": "Visitante Marca pelo menos Um Gol(s)",
    "Home/Away": "Casa/Visitante",
    "Over/Under": "Total de Gol(s) no Encontro, Acima/Abaixo",
    "Clean Sheet - Home": "Time da Casa NÃO Tomará Gol(s)",
    "Clean Sheet - Away": "Time Visitante NÃO Tomará Gol(s)",
    "Results/Both Teams To Score": "Resultado/2 Times Marcam",
    "Home Team Score a Goal": "Time da Casa Marca",
    "Exact Goals Number": "Número Exato de Gol(s)",
    "Odd/Even": "Placar Impar/Par",
}

"""
Excludes:
Acreano
Alagoano
Amazonense
Baiano 1
Baiano 2
Brasiliense
Copa Nordeste
Capixaba
Carioca 2
Catarinense 1
Cearense 1
Cearense 2
Gaucho 1
Gaucho 2
Goiano 1
Maranhense
Matrogrossense
Mineiro 1
Mineiro 2
Paraense
Paraibano
Paranaense 1
Paranaense 2
Paulista A2
Paulista A3
Pernabucano 1
Piauiense
Portiguar
Rondoniense
Roraimense
Sergipano
Sul Matogrossense
Tocansinense
Amapaense
Brasileiro U20
Copa Verde
Sao Paolo Youth Cup

"""
INVALID_ALL_COTES_CHAMPIONSHIPS = [
    1288,
    1289,
    1290,
    1291,
    1292,
    1293,
    1294,
    1295,
    1298,
    1299,
    1300,
    1301,
    1302,
    1303,
    1304,
    1305,
    1306,
    1307,
    1308,
    1309,
    1310,
    1311,
    1312,
    1314,
    1315,
    1316,
    1317,
    1318,
    1319,
    1320,
    1321,
    1322,
    1323,
    1324,
    1385,
    1386,
    1456,
]

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
        "More": "Mais de",
        "Odd": "Impar",
        "Even" : "Par",
        "more" : "Mais de"
    }

    for i in COTATION_NAME.keys():
        if i in string:
            string = string.replace(i, COTATION_NAME[i])
            string = string + " " + total
    return string


TOKEN = 'DLHVB3IPJuKN8dxfV5ju0ajHqxMl4zx91u5zxOwLS8rHd5w6SjJeLEOaHpR5'


def check_request_status(request):
    if not request.status_code == 200:
        print('Falha: Url:' + request.url)
        print('Status: ' + request.status_code)


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


def consuming_game_cotation_api():

    before_time = tzlocal.now() - datetime.timedelta(days=2)

    before_year = before_time.year
    before_month = before_time.month
    before_day = before_time.day
    
    after_time = tzlocal.now() + datetime.timedelta(days=10)

    after_year = after_time.year
    after_month = after_time.month
    after_day = after_time.day


    first_date = str(before_year) + "-" + str(before_month) + "-" + str(before_day)
    second_date = str(after_year) + "-" +str(after_month) + "-" + str(after_day)


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
    
    processing_cotations_v2()
    process_tickets()
    


def process_json_games_cotations(json_response):
    
    if GeneralConfigurations.objects.filter(pk=1):
        max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
    else:
        max_cotation_value = 200
    games_array = json_response.get('data')
    for game in games_array:

   

        if Game.objects.filter(pk=game['id']).exists():
            ft_score = game['scores']['ft_score']
            if not ft_score or ft_score == None:
                ft_score = F('ft_score')
            Game.objects.filter(pk=game['id']).update(
                name=game['localTeam']['data']['name'] +
                " x " + game['visitorTeam']['data']['name'],
                status_game=game['time']['status'],                
                ht_score=game['scores']['ht_score'],
                ft_score=ft_score,
                odds_calculated=game['winning_odds_calculated'],
                start_game_date=datetime.datetime.strptime(
                game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"))
        else:
            Game.objects.create(pk=game['id'],
                name=game['localTeam']['data']['name'] +
                " x " + game['visitorTeam']['data']['name'],
                status_game=game['time']['status'],                
                ht_score=game['scores']['ht_score'],
                ft_score=game['scores']['ft_score'],
                odds_calculated=game['winning_odds_calculated'],
                start_game_date=datetime.datetime.strptime(
                game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
                championship=Championship.objects.get(pk=game["league_id"]))
        save_odds(game['id'], game['odds'], max_cotation_value)
    


def get_bet365_from_bookmakers(bookmakers):

    for bookmaker in bookmakers:
        if int(bookmaker['id']) == 2:
            return bookmaker
    return bookmakers[0]


def can_save_this_market(kind_name, championship_id, processed_markets):
    if championship_id in INVALID_ALL_COTES_CHAMPIONSHIPS:
        if kind_name in MARKET_NAME_SMALL_TEAMS.keys() and kind_name not in processed_markets:
            return True
    elif kind_name in MARKET_NAME.keys() and kind_name not in processed_markets:
        return True
    return False

def save_odds(game_id, odds, max_cotation_value):

    odds_array = odds.get('data')
    game_instance = Game.objects.get(pk=game_id)
    championship_id = game_instance.championship_id
    processed_markets = []

    for market in odds_array:
        kind_name = market['name']
        if can_save_this_market(kind_name, championship_id, processed_markets):
            bookmakers = market['bookmaker']['data']
            bookmaker = get_bet365_from_bookmakers(bookmakers)
            cotations = bookmaker['odds']['data']

            for cotation in cotations:

                cotation_value = max_cotation_value if float(cotation['value']) > max_cotation_value else float(cotation['value'])
                cotation_name = renaming_cotations(cotation['label'], " " if cotation['total'] == None else cotation['total']).strip()
                is_standard=False
                cotation_label = cotation['label']

                if kind_name == '3Way Result' and cotation['label'] in ['1', '2', 'X']:
                    is_standard=True
                if kind_name == 'Result/Total Goals':
                    cotation_name = renaming_cotations(cotation['label'], " ").strip()
                if kind_name == 'Double Chance' and cotation['label'] in ['12','1X','X2']:
                    if cotation_label == '1X':
                        cotation_name = 'Casa/Empate'
                    elif cotation_label == '2X':
                        cotation_name = 'Visitante/Empate'
                    else:
                        cotation_name = 'Casa/Visitante'
                

                Cotation(name=cotation_name,
                            value=cotation_value,
                            original_value=cotation_value,
                            game=game_instance,
                            is_standard=is_standard,
                            total=cotation['total'],
                            winning=cotation['winning'],
                            kind=MARKET_NAME.setdefault(kind_name, kind_name)).save()
                            
            processed_markets.append(kind_name)


def process_tickets():
    tickets_to_process = BetTicket.objects.filter(bet_ticket_status='Aguardando Resultados')
    for ticket in tickets_to_process:
        ticket.update_ticket_status()

def processing_cotations_v2():

    print("Processando resultados.")

    games_to_process = Game.objects.annotate(cotations_count=Count('cotations')).filter(
        status_game="FT", odds_processed=False, ft_score__isnull=False,
        cotations_count__gt=0).exclude(ft_score='')
        
    print(games_to_process.count(), '\n')

    for game in games_to_process:
        local_team_score = int(game.ft_score.split('-')[0])
        visitor_team_score = int(game.ft_score.split('-')[1])
        #not_calculaded_cotations = game.cotations.filter(winning__isnull=True)
        print("Jogo:" + str(game.name) + " ID: " + str(game.pk))

        not_calculaded_cotations = game.cotations
        vencedor_encontro(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        casa_visitante(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        dupla_chance(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        vencer_e_nao_tomar_gol(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        etapa_com_mais_gol(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        vencedor_nas_duas_etapas(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        numero_exato_de_gols(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        resultado_e_2_times_marcam(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        resultado_e_total_de_gols(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        total_de_gols_impar_par(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        resultado_exato_primeiro_tempo(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        os_dois_times_marcam(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        vencedor_primeiro_tempo(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        total_gols_visitante(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        total_gols_casa(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        total_gols_primeiro_tempo_acima_abaixo(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        resultado_exato(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        visitante_marca_pelo_menos_um_gol(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        total_gols_encontro_acima_abaixo(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        time_casa_nao_tomara_gols(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        time_visitante_nao_tomara_gols(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        time_casa_marca(game, not_calculaded_cotations, local_team_score, visitor_team_score)
        game.odds_processed=True
        game.save()


def vencedor_encontro(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Vencedor do Encontro')
    

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > visitor_team_score:
            cotations.filter(name='1').update(winning=True)			
        elif local_team_score < visitor_team_score:			
            cotations.filter(name='2').update(winning=True)			
        else:	
            cotations.filter(name='X').update(winning=True)


def casa_visitante(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Casa/Visitante')
    
    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > visitor_team_score:
            cotations.filter(name='1').update(winning=True)
        elif local_team_score < visitor_team_score:		
            cotations.filter(name='2').update(winning=True)


def dupla_chance(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Dupla Chance')

    if cotations.count() > 0:
        cotations.update(winning=False)
        casa_empate = cotations.filter(name='Casa/Empate')
        casa_visitante = cotations.filter(name='Casa/Visitante')
        empate_visitante = cotations.filter(name='Empate/Visitante')
    
        if local_team_score > visitor_team_score:
            casa_empate.update(winning=True)
            casa_visitante.update(winning=True)
        elif local_team_score < visitor_team_score:
            casa_visitante.update(winning=True)
            empate_visitante.update(winning=True)
        else:
            casa_empate.update(winning=True)
            empate_visitante.update(winning=True)


def vencer_e_nao_tomar_gol(game, all_cotations,local_team_score,visitor_team_score):
    
    cotations = all_cotations.filter(kind='Vencer e não tomar Gol(s)')

    if cotations.count() > 0:
        cotations.update(winning=False)
        if local_team_score > visitor_team_score:
            if visitor_team_score == 0:
                cotations.filter(name='1').update(winning=True)
        elif local_team_score < visitor_team_score:
            if local_team_score == 0:
                cotations.filter(name='2').update(winning=True)   


def etapa_com_mais_gol(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Etapa com Mais Gol(s)')


    if cotations.count() > 0:

        casa_placar_1, visitante_placar_1 = game.ht_score.split('-')
        casa_placar_2, visitante_placar_2 = (local_team_score,visitor_team_score)
        result_1_etapa = int(casa_placar_1) +  int(visitante_placar_1)
        result_2_etapa = ( int(casa_placar_2) + int(visitante_placar_2) ) - result_1_etapa
        cotations.update(winning=False)

        if result_1_etapa > result_2_etapa:        
            cotations.filter(name='1° Tempo').update(winning=True)                                              
        elif result_1_etapa < result_2_etapa:                            
            cotations.filter(name='2° Tempo').update(winning=True)                      
        else:                        
            cotations.filter(name='X').update(winning=True)                     


def vencedor_nas_duas_etapas(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Vencedor nas Duas Etapas')

    
    if cotations.count() > 0:

        casa_placar_1, visitante_placar_1 = game.ht_score.split('-')
        casa_placar_2, visitante_placar_2 = (local_team_score,visitor_team_score)
        result_1_etapa = int(casa_placar_1) - int(visitante_placar_1)
        result_2_etapa = int(casa_placar_2) - int(visitante_placar_2)
        cotations.update(winning=False)

        if result_1_etapa > 0 and result_2_etapa > 0:           
            cotations.filter(name='1').update(winning=True)

        elif result_1_etapa < 0 and result_2_etapa < 0:        
            cotations.filter(name='2').update(winning=True)             


def numero_exato_de_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Número Exato de Gol(s)')

    
    if cotations.count() > 0:
        
        casa_placar, visitante_placar = (local_team_score,visitor_team_score)
        result = int(casa_placar) + int(visitante_placar)
        cotations.update(winning=False)

        if result > 7:        
            cotations.filter(name='Mais de 7').update(winning=True)
        else:
            cotations.filter(name=str(result)).update(winning=True)    


def intervalo_e_final_de_jogo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Intervalo/Final de Jogo')

    if cotations.count() > 0:

        casa_placar_1, visitante_placar_1 = game.ht_score.split('-')
        casa_placar_2, visitante_placar_2 = (local_team_score,visitor_team_score)
        result_1_etapa = int(casa_placar_1) - int(visitante_placar_1)
        result_2_etapa = int(casa_placar_2) - int(visitante_placar_2)
        localTeam = game.name.split('x')[0].strip()
        visitorTeam = game.name.split('x')[1].strip()
        cotations.update(winning=False)
        
        if result_1_etapa > 0:
            if result_2_etapa > 0:            
                cotations.filter(name=str(localTeam+"/"+localTeam)).update(winning=True)            
            elif result_2_etapa < 0:            
                cotations.filter(name=str(localTeam+"/"+visitorTeam)).update(winning=True)            
            else:            
                cotations.filter(name=str(localTeam+"/Empate")).update(winning=True)            
                

        elif result_1_etapa < 0:
            if result_2_etapa > 0:            
                cotations.filter(name=str(visitorTeam+"/"+localTeam)).update(winning=True)                                    
            elif result_2_etapa < 0:            
                cotations.filter(name=str(visitorTeam+"/"+visitorTeam)).update(winning=True)            
            else:            
                cotations.filter(name=str(visitorTeam+"/Empate")).update(winning=True)            

        else:
            if result_2_etapa > 0:            
                cotations.filter(name=str("Empate/"+localTeam)).update(winning=True)                        
            elif result_2_etapa < 0:            
                cotations.filter(name=str("Empate/"+visitorTeam)).update(winning=True)                                
            else:            
                cotations.filter(name="Empate/Empate").update(winning=True)


def resultado_e_2_times_marcam(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Resultado/2 Times Marcam')

    
    if cotations.count() > 0:

        casa_placar, visitante_placar = (local_team_score,visitor_team_score)
        result = int(casa_placar) - int(visitante_placar)
        cotations.update(winning=False)

        if result > 0:
            if local_team_score > 0 and visitor_team_score > 0:                                   
                cotations.filter(name="Casa/Sim").update(winning=True)                          

            else:            
                cotations.filter(name="Casa/Não").update(winning=True)

        elif result < 0:
            if local_team_score > 0 and visitor_team_score > 0:                                   
                cotations.filter(name="Visitante/Sim").update(winning=True)
                
            else:
                cotations.filter(name="Visitante/Não").update(winning=True)                         

        else:
            if local_team_score > 0 and visitor_team_score > 0:                                   
                cotations.filter(name="Empate/Sim").update(winning=True)

            else:            
                cotations.filter(name="Empate/Não").update(winning=True)                            


def resultado_e_total_de_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind="Resultado/Total de Gol(s)")

    if cotations.count() > 0:
        casa_placar, visitante_placar = (local_team_score,visitor_team_score)
        result = int(casa_placar) - int(visitante_placar)
        total_gols = int(casa_placar) + int(visitante_placar)
        cotations.update(winning=False)

        if result > 0:
            cotations.filter(name__contains="Casa/Acima", total__lt=total_gols).update(winning=True)
            cotations.filter(name__contains="Casa/Abaixo", total__gt=total_gols).update(winning=True)
        elif result < 0:
            cotations.filter(name__contains="Visitante/Acima", total__lt=total_gols).update(winning=True)
            cotations.filter(name__contains="Visitante/Abaixo", total__gt=total_gols).update(winning=True)
        else:
            cotations.filter(name__contains="Empate/Acima", total__lt=total_gols).update(winning=True)
            cotations.filter(name__contains="Empate/Abaixo", total__gt=total_gols).update(winning=True)          


def total_de_gols_impar_par(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind="Placar Impar/Par")
           
    if cotations.count() > 0:

        total_gols = int((local_team_score,visitor_team_score)[0]) + int((local_team_score,visitor_team_score)[1])
        cotations.update(winning=False)

        if total_gols == 0 or total_gols % 2 == 0:
            cotations.filter(name="Par").update(winning=True)
        else:
            cotations.filter(name="Impar").update(winning=True)


def resultado_exato_primeiro_tempo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Resultado Exato no Primeiro Tempo')

    if cotations.count() > 0:
        cotations.update(winning=False)
        etapa_1_resultado = game.ht_score.replace('-',':')
        winners = cotations.filter(name=etapa_1_resultado)
        winners.update(winning=True)


def os_dois_times_marcam(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='2 Times Marcam')

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > 0 and visitor_team_score > 0:
            cotations.filter(name='Sim').update(winning=True)
        else:
            cotations.filter(name='Não').update(winning=True)


def vencedor_primeiro_tempo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Vencedor do Primeiro Tempo')

    if cotations.count() > 0:
        cotations.update(winning=False)

        casa_placar, visita_placar = game.ht_score.split('-')
        casa_placar = int(casa_placar)
        visita_placar = int(visita_placar)

        if casa_placar > visita_placar:
            cotations.filter(name='1').update(winning=True)
        elif casa_placar < visita_placar:
            cotations.filter(name='2').update(winning=True)
        else:
            cotations.filter(name='X').update(winning=True)


def total_gols_visitante(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Total de Gols do Visitante')

    if cotations.count() > 0:
        cotations.update(winning=False)
        cotations.filter(name__contains='Acima', total__lt=visitor_team_score).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=visitor_team_score).update(winning=True)


def total_gols_casa(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Total de Gols da Casa')

    if cotations.count() > 0:
        cotations.update(winning=False)
        cotations.filter(name__contains='Acima', total__lt=local_team_score).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=local_team_score).update(winning=True)



def total_gols_primeiro_tempo_acima_abaixo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Total de Gols do Primeiro Tempo, Acima/Abaixo')

    if cotations.count() > 0:
        cotations.update(winning=False)
        casa_placar, visita_placar = game.ht_score.split('-')
        placar_total_etapa_1 = float(casa_placar) + float(visita_placar)
        
        cotations.filter(name__contains='Acima', total__lt=placar_total_etapa_1).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=placar_total_etapa_1).update(winning=True)



def resultado_exato(game, all_cotations,local_team_score,visitor_team_score):
    cotations = all_cotations.filter(kind='Resultado Exato')

    if cotations.count() > 0:
        result_ft = game.ft_score.replace('-',':')
        cotations.update(winning=False)
        winners = cotations.filter(name=result_ft)
        winners.update(winning=True)


def visitante_marca_pelo_menos_um_gol(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Visitante Marca pelo menos Um Gol(s)')

    if cotations.count() > 0:
        cotations.update(winning=False)
        if visitor_team_score > 0:
            cotations.filter(name='Sim').update(winning=True)
        else:
            cotations.filter(name='Não').update(winning=True)



def total_gols_encontro_acima_abaixo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Total de Gol(s) no Encontro, Acima/Abaixo')

    if cotations.count() > 0:
        cotations.update(winning=False)
        casa_placar, visita_placar = (local_team_score,visitor_team_score)
        placar_total = float(casa_placar) + float(visita_placar)
        
        cotations.filter(name__contains='Acima', total__lt=placar_total).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=placar_total).update(winning=True)


def time_casa_nao_tomara_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Time da Casa NÃO Tomará Gol(s)')

    if cotations.count() > 0:
        cotations.update(winning=False)

        if visitor_team_score > 0:
            cotations.filter(name='Não').update(winning=True)
        else:
            cotations.filter(name='Sim').update(winning=True)


def time_visitante_nao_tomara_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Time Visitante NÃO Tomará Gol(s)')

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > 0:
            cotations.filter(name='Não').update(winning=True)
        else:
            cotations.filter(name='Sim').update(winning=True)



def time_casa_marca(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind='Time da Casa Marca')

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > 0:
            cotations.filter(name='Sim').update(winning=True)
        else:
            cotations.filter(name='Não').update(winning=True)
