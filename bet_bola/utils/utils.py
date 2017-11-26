from core.models import Championship,Game,Cotation


def populating_bd():
	Championship.consuming_api()
	Game.consuming_api()
	Cotation.consuming_api()

def updating_games():
	Game.consuming_api()
