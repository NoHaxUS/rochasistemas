from core.models import Championship,Game,Cotation
from datetime import datetime

def populating_bd():
	first_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day))
	second_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day + 7))

	Championship.consuming_api()
	Game.consuming_api(first_date,second_date)
	Cotation.consuming_api()

def updating_games():
	first_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day))
	second_date = str(datetime.now().year) + "-" +str(datetime.now().month) + "-" + str((datetime.now().day + 2))
	Game.consuming_api(first_date,second_date)
	Cotation.consuming_api()