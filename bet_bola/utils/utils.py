from core.models import Championship,Game,Cotation,BetTicket
from datetime import datetime

def populating_bd():
	first_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day))
	second_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day + 7))

	Championship.consuming_api()
	Game.consuming_api(first_date,second_date)
	Cotation.consuming_api()
	Cotation.processing_cotations()
	BetTicket.processing_tickets()

def updating_games():
	first_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day-3))
	second_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day))
	
	Championship.consuming_api()
	Game.consuming_api(first_date,second_date)
	Cotation.consuming_api()
	Cotation.processing_cotations()
	BetTicket.processing_tickets()

	

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