from core.models import *
from user.models import GeneralConfigurations
import requests

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
}



def renaming_cotations(string, total):

	COTATION_NAME = {
	"Under": "Abaixo",
	"Over": "Acima",
	"Draw": "Empate",
	"Away": "Visitante",
	"Home": "Casa",
	"1st Half":"1° Tempo",
	"2nd Half":"2° Tempo",
	"No":"Não",
	"Yes":"Sim",
	"More":"Mais de"
	}

	for i in COTATION_NAME.keys():
		if i in string:
			string = string.replace(i, COTATION_NAME[i])
			string = string +" "+ total
	return string

TOKEN = 'DLHVB3IPJuKN8dxfV5ju0ajHqxMl4zx91u5zxOwLS8rHd5w6SjJeLEOaHpR5'


def consuming_championship_api():

	request = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token=" +
						   TOKEN + "&include=country&tz=America/Santarem")

	if not request.status_code == 200:
		print('Falha ao buscar campeonatos')
		print(request.status_code)

	print("Atualizando Campeonatos")
	json_response = request.json()
	championship_array = json_response.get('data')

	if championship_array:
		for championship in championship_array:
			Championship(pk=championship['id'], name=championship['name'],
							 country=championship['country']['data']['name']).save()
	else:
		print("O array de campeonatos retornou vazio.")
	
	consuming_game_cotation_api()


def consuming_game_cotation_api():
	first_date = "2018-01-27"
	second_date = "2018-01-30"
	print("Atualizando os Games")
	request = requests.get(
		'https://soccer.sportmonks.com/api/v2.0/fixtures/between/'+first_date+'/'+second_date+'?api_token='+TOKEN+'&include=localTeam,visitorTeam,odds&tz=America/Santarem')
	
	pages = request.json().get('meta')['pagination']['total_pages']

	for i in range(1, pages):
		if not request.status_code == 200:
			print('Falha ao atualizar Jogos')
			print(request.status_code)

		json_response = request.json()
		games_array = json_response.get('data')

		for game in games_array:

			Game(pk=game['id'],
				 name=game['localTeam']['data']['name'] + " x " + game['visitorTeam']['data']['name'],
				 status_game=game['time']['status'],
				 local_team_score=game['scores']['localteam_score'],
				 visitor_team_score=game['scores']['visitorteam_score'],
				 ht_score=game['scores']['ht_score'],
				 ft_score=game['scores']['ft_score'],
				 odds_calculated=game['winning_odds_calculated'],
				 start_game_date=datetime.strptime(
					 game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
				 championship=Championship.objects.get(pk=game["league_id"])).save()

			save_odds(game['id'], game['odds'])

		request = requests.get('https://soccer.sportmonks.com/api/v2.0/fixtures/between/'+first_date+'/'+second_date+'?page='+str((i+1))+'&api_token='+TOKEN+'&include=localTeam,visitorTeam,odds&tz=America/Santarem')

def get_bet365_from_bookmakers(bookmakers):

	for bookmaker in bookmakers:
		if bookmaker['id'] == 2:
			return bookmaker

	return bookmakers[0]


def save_odds(game_id, odds):

	if GeneralConfigurations.objects.filter(pk=1):
		max_cotation_value = GeneralConfigurations.objects.get(
			pk=1).max_cotation_value
	else:
		max_cotation_value = 200

	odds_array = odds.get('data')

	game_instance = Game.objects.get(pk=game_id)

	for market in odds_array:

		kind_name = market['name']
		if kind_name in MARKET_NAME.keys():
			bookmakers = market['bookmaker']['data']

			bookmaker = get_bet365_from_bookmakers(bookmakers)
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



def processing_cotations():
	for game in Game.objects.filter(status_game='FT'):			
		print(game.pk, game.name)
		#dento do if só entra games q tenham os dados do score ok
		try:
			if game.is_able():							
				#nesse conjunto de if,elif e else são processados 4 markets			
				#Vencedor do Encontro, Casa/Visitante, Dupla Chance,Vencedor Não tomará Gol(s) 		
				cotations = game.cotations.filter(kind='Vencedor do Encontro') 
				if game.visitor_team_score > game.local_team_score:					
					cotations.update(winning=False)									
					c2 = cotations.filter(name='2')					
					c2.update(winning= True)					
					cotations = game.cotations.filter(kind='Casa/Visitante')
					cotations.filter(name='1').update(winning=False)
					cotations.filter(name='2').update(winning=True)					
					if game.cotations.filter(kind='Dupla Chance').count()>0:
						cotations = game.cotations.filter(kind='Dupla Chance')
						cotations.update(winning=True)					
						cotations.filter(name='Casa/Empate').update(winning=False)
						

					if game.cotations.filter(kind='Vencedor Não tomará Gol(s)').count()>0:
						cotations = game.cotations.filter(kind='Vencedor Não tomará Gol(s)')
						cotations.update(winning=True)
						if game.local_team_score > 0:
							cotations.filter(name='2').update(winning=True)							


				elif game.visitor_team_score < game.local_team_score:
					cotations.update(winning=False)
					cotations.filter(name='1').update(winning=True)					
					cotations = game.cotations.filter(kind='Casa/Visitante')
					cotations.filter(name='1').update(winning=True)
					cotations.filter(name='2').update(winning=False)
					
					if game.cotations.filter(kind='Dupla Chance').count()>0:
						cotations = game.cotations.filter(kind='Dupla Chance')					
						cotations.update(winning=True)
						cotations.filter(name='Empate/Visitante').update(winning=False)						

					if game.cotations.filter(kind='Vencedor Não tomará Gol(s)').count()>0:
						cotations = game.cotations.filter(kind='Vencedor Não tomará Gol(s)')
						cotations.update(winning=True)
						if game.visitor_team_score > 0:
							cotations.filter(name='1').update(winning=True)							

				else:
					cotations.update(winning=False)					
					cotations.filter(name='X').update(winning=True)															
					cotations = game.cotations.filter(kind='Casa/Visitante')
					cotations.filter(name='1').update(winning=False)
					cotations.filter(name='2').update(winning=False)									
					if game.cotations.filter(kind='Dupla Chance').count()>0:
						cotations = game.cotations.filter(kind='Dupla Chance')
						cotations.update(winning=True)
						c = cotations.filter(name='Casa/Visitante').update(winning=False)
						
				#dentro desse if é tradado o market Etapa com Mais Gol(s)
				if game.cotations.filter(kind='Etapa com Mais Gol(s)').count()>0:
					cotations = game.cotations.filter(kind='Etapa com Mais Gol(s)')
					result_1_etapa = int(game.ht_score.split('-')[0]) +  int(game.ht_score.split('-')[1])
					result_2_etapa = (int(game.ft_score.split('-')[0]) - int(game.ht_score.split('-')[0])) + (int(game.ft_score.split('-')[1]) - int(game.ht_score.split('-')[1]))
					if result_1_etapa > result_2_etapa:
						cotations.update(winning=False)
						cotations.filter(name='1° Tempo').update(winning=True)												

					elif result_1_etapa < result_2_etapa:
						cotations.update(winning=False)						
						cotations.filter(name='2° Tempo').update(winning=True)						

					else:
						cotations.update(winning=False)						
						cotations.filter(name='X').update(winning=True)						

				#dentro desse if é tradado o market Vencendor nas Duas Etapas								
				if game.cotations.filter(kind='Vencedor nas Duas Etapas').count()>0:
					result_1_etapa = int(game.ht_score.split('-')[0]) - int(game.ht_score.split('-')[1])
					result_2_etapa = int(game.ft_score.split('-')[0]) - int(game.ft_score.split('-')[1])
					cotations = game.cotations.filter(kind='Vencedor nas Duas Etapas')
					if result_1_etapa > 0 and result_2_etapa > 0:			
						cotations.filter(name='1').update(winning=True)
						c1 = cotations.filter(name='2').update(winning=False)				

					elif result_1_etapa < 0 and result_2_etapa < 0:
						cotations.filter(name='1').update(winning=False)
						cotations.filter(name='2').update(winning=True)				
						
					else:
						cotations.filter(name='1').update(winning=False)
						cotations.filter(name='2').update(winning=False)

				#dentro desse if é tradado o market Número Exato de Gol(s)
				if game.cotations.filter(kind='Número Exato de Gol(s)').count()>0:
					result = int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1])
					cotations = game.cotations.filter(kind='Número Exato de Gol(s)')
					
					if result >= 7:
						cotations.update(winning=False)
						cotations.filter(name='more 7').update(winning=True)

					else:
						cotations.update(winning=False)
						cotations.filter(name=str(result)).update(winning=True)
						

				#dentro desse if é tradado o market Intervalo/Final de Jogo
				if game.cotations.filter(kind='Intervalo/Final de Jogo').count()>0:
					result_1_etapa = int(game.ht_score.split('-')[0]) - int(game.ht_score.split('-')[1])
					result_2_etapa = int(game.ft_score.split('-')[0]) - int(game.ft_score.split('-')[1])
					cotations = game.cotations.filter(kind='Intervalo/Final de Jogo')
					localTeam = game.name.split('x')[0].strip()
					visitorTeam = game.name.split('x')[1].strip()

					if result_1_etapa > 0:
						if result_2_etapa > 0:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in localTeam and c.name.split("/")[1].strip() in localTeam:
									c.winning = True
									c.save()
						elif result_2_etapa < 0:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in localTeam and c.name.split("/")[1].strip() in visitorTeam:
									c.winning = True
									c.save()							
						else:
							cotations.update(winning=False)							
							for c in cotations.all():
								if c.name.split("/")[0].strip() in localTeam and c.name.split("/")[1].strip() in "Empate":
									c.winning = True
									c.save()							

					elif result_1_etapa < 0:
						if result_2_etapa > 0:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in visitorTeam and c.name.split("/")[1].strip() in localTeam:
									c.winning = True
									c.save()							
							
						elif result_2_etapa < 0:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in visitorTeam and c.name.split("/")[1].strip() in visitorTeam:
									c.winning = True
									c.save()							

						else:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in visitorTeam and c.name.split("/")[1].strip() in "Empate":
									c.winning = True
									c.save()														

					else:
						if result_2_etapa > 0:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in "Empate" and c.name.split("/")[1].strip() in localTeam:
									c.winning = True
									c.save()							
							
						elif result_2_etapa < 0:
							cotations.update(winning=False)
							for c in cotations.all():
								if c.name.split("/")[0].strip() in "Empate" and c.name.split("/")[1].strip() in visitorTeam:
									c.winning = True
									c.save()							
							
						else:
							cotations.update(winning=False)
							cotations.filter(name="Empate"+"/"+"Empate").update(winning=True)
							

				#dentro desse if é tradado 2 markets Resultado/2 Times Marcam e Resultado/Total de Gol(s)
				if game.cotations.filter(kind='Resultado/2 Times Marcam').count()>0:
					cotations = game.cotations.filter(kind='Resultado/2 Times Marcam')
					result = int(game.ft_score.split('-')[0]) - int(game.ft_score.split('-')[1])
					if result > 0:
						if game.local_team_score > 0 and game.visitor_team_score > 0:						
							cotations.update(winning=False)
							cotations.filter(name="Casa/Sim").update(winning=True)							

						else:
							cotations.update(winning=False)
							cotations.filter(name="Casa/Não").update(winning=True)
							
						
						if game.cotations.filter(kind="Resultado/Total de Gol(s)").count()>0:
								cotations = game.cotations.filter(kind="Resultado/Total de Gol(s)")			
								cotations.update(winning=False)					
								for c in cotations.filter(name="Casa/Acima"):
									if c.total < int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1]):										
										c.winning = True
										c.save()				

								for c in cotations.filter(name="Casa/Abaixo"):
									if c.total > int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1]):										
										c.winning = True
										c.save()				

					elif result < 0:
						if game.local_team_score > 0 and game.visitor_team_score > 0:						
							cotations.update(winning=False)
							cotations.filter(name="Visitante/Sim").update(winning=True)
							
						else:
							cotations.update(winning=False)
							cotations.filter(name="Visitante/Não").update(winning=True)							

						if game.cotations.filter(kind="Resultado/Total de Gol(s)").count()>0:
								cotations = game.cotations.filter(kind="Resultado/Total de Gol(s)")			
								cotations.update(winning=False)					
								for c in cotations.filter(name="Visitante/Acima"):
									if c.total < int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1]):										
										c.winning = True
										c.save()								

								for c in cotations.filter(name="Visitante/Abaixo"):
									if c.total > int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1]):										
										c.winning = True
										c.save()

					else:
						if game.local_team_score > 0 and game.visitor_team_score > 0:						
							cotations.update(winning=False)
							cotations.filter(name="Empate/Sim").update(winning=True)

						else:
							cotations.update(winning=False)
							cotations.filter(name="Empate/Não").update(winning=True)							
							
						if game.cotations.filter(kind="Resultado/Total de Gol(s)").count()>0:
								cotations = game.cotations.filter(kind="Resultado/Total de Gol(s)")			
								cotations.update(winning=False)					
								for c in cotations.filter(name="Empate/Acima"):
									if c.total < int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1]):										
										c.winning = True
										c.save()								

								for c in cotations.filter(name="Empate/Abaixo"):
									if c.total > int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1]):										
										c.winning = True
										c.save()				
		except RuntimeError:
			continue			
		finally:
			pass
