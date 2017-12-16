from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from .manager import GamesManager,CotationsManager
from user.models import Seller
from django.contrib.auth.models import User
from django.utils import timezone
import requests
import decimal
# Create your models here.

TOKEN='OOabOgBw4awrsYQ51DIWz3i4ILKWxBAXqLQI5b01xzZuoKhyBHCcdINUbIeM'

BET_TICKET_STATUS = (
		('WAITING_RESULT', 'Aguardando Resultados.'),
		('NOT_WON', 'Não Venceu.'),
		('WON', 'Venceu.'),
	)

REWARD_STATUS = (
		('WAITING_RESULTS', 'Aguardando Resultados.'),
		('PAID', 'Finalizado, O apostador foi pago.'),
		('NOT_WON', 'Esse ticket não venceu.'),
		('WON', 'Venceu, Aguardando pagamento.'),
	)

GAME_STATUS = (
		('NS', 'Not Started'),
		('LIVE','Live'),
		('HT', 'Half-time'),
		('FT', 'Full-Time')	,	
		('ET', 'Extra-Time'),
		('PEN_LIVE', 'Penalty Shootout'),
		('AET', 'Finished after extra time'),
		('BREAK', 'Match finished, waiting for extra time to start'),
		('FT_PEN', 'Full-Time after penalties'),
		('CANCL', 'Cancelled'),
		('POSTP', 'PostPhoned'),
		('INT',	'Interrupted'),
		('ABAN', 'Abandoned'),
		('SUSP', 'Suspended'),
		('AWARDED', 'Awarded'),
		('DELAYED', 'Delayed'),
		('TBA', 'To Be Announced (Fixture will be updated with exact time later)'),
		('WO', 'Walkover (Awarding of a victory to a contestant because there are no other contestants)'),
	)


PAYMENT_STATUS = (
		('WATING_PAYMENT', 'Aguardando Pagamento do Ticket.'),
		('PAID', 'Pago.'),
	)


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
	"Corners Over Under": "Escanteios, Acima/Abaixo",
	"HT/FT Double": "Intervalo/Final de Jogo",
	"Results/Both Teams To Score": "Resultado/2 Times Marcam",
	"Home Team Score a Goal": "Time da casa Marca",
	"Win Both Halves": "Vencedor nas Duas Etapas",
	"Exact Goals Number": "Número Exato de Gol(s)",
}	



class BetTicket(models.Model):	
	user = models.ForeignKey('auth.User', related_name='my_bet_tickets')
	seller = models.ForeignKey('user.Seller', null=True, related_name='bet_tickets_validated_by_me')
	cotations = models.ManyToManyField('Cotation', related_name='my_bet_tickets')
	creation_date = models.DateTimeField(auto_now_add=True)	
	reward = models.ForeignKey('Reward', default=None)
	payment = models.OneToOneField('Payment', default=None)
	value = models.DecimalField(max_digits=6, decimal_places=2)
	bet_ticket_status = models.CharField(max_length=80, choices=BET_TICKET_STATUS,default=BET_TICKET_STATUS[0][1])


	def ticket_valid(self, user):
		self.payment.status_payment = PAYMENT_STATUS[1][1]
		self.payment.who_set_payment = Seller.objects.get(pk=user.pk)
		self.payment.save()

	def reward_payment(self, user):
		self.reward.status_reward = REWARD_STATUS[1][1]
		self.reward.who_rewarded = Seller.objects.get(pk=user.pk)
		self.reward.save()

	def cota_total(self):
		cota_total = 1
		
		for cotation in self.cotations.all():
			cota_total *= cotation.value
		
		return cota_total

	def __str__(self):
		return str(self.pk)

	class Meta:
		verbose_name = 'Ticket'
		verbose_name_plural = 'Tickets'
		permissions = (
				('can_validate_payment', "Can validate user ticket"),
				('can_reward', "Can reward a user"),
			)


class Game(models.Model):
	name = models.CharField(max_length=80)	
	start_game_date = models.DateTimeField()
	championship = models.ForeignKey('Championship',related_name='my_games')
	status_game = models.CharField(max_length=80,default=GAME_STATUS[0][1], choices=GAME_STATUS)
	objects = GamesManager()
	
	@staticmethod
	def consuming_api(first_date, second_date):
		r = requests.get("https://soccer.sportmonks.com/api/v2.0/fixtures/between/"+first_date+"/"+second_date+"?api_token="+TOKEN+"&include=localTeam,visitorTeam")
	
		for i in range(1,r.json().get('meta')['pagination']['total_pages']):			

			for game in r.json().get('data'):
				if Championship(pk = game["league_id"]) in Championship.objects.all():
					if Game(pk = game["id"]) in Game.objects.all():
						g = Game.objects.get(pk = game["id"])
						g.status_game = game['time']['status']
						g.save()
						
					else:
						Game(pk=game['id'],
							start_game_date=datetime.strptime(game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
							name=game['localTeam']['data']['name']+" x " +game['visitorTeam']['data']['name'], championship=Championship.objects.get(pk=game["league_id"]), status_game=game['time']["status"]).save() 

			r = requests.get("https://soccer.sportmonks.com/api/v2.0/fixtures/between/"+first_date+"/"+second_date+"?page="+str((i+1))+"&api_token="+TOKEN+"&include=localTeam,visitorTeam")
	
	class Meta:
		verbose_name = 'Jogo'
		verbose_name_plural = 'Jogos'

	def __str__(self):
		return self.name	


class Championship(models.Model):
	name = models.CharField(max_length=80)

	@staticmethod
	def consuming_api():
		r = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token="+TOKEN)
		
		for championship in r.json().get('data'):
			Championship(pk=championship['id'],name = championship['name']).save()

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Campeonato'
		verbose_name_plural = 'Campeonatos'



class Reward(models.Model):
	who_rewarded = models.ForeignKey('user.Seller', null=True)
	reward_date = models.DateTimeField(null=True, auto_now=True)
	value = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	status_reward = models.CharField(max_length=80, choices=REWARD_STATUS, default=REWARD_STATUS[0][1])

	class Meta:
		verbose_name = 'Recompensa'
		verbose_name_plural = 'Recompensas'


class Cotation(models.Model):
	name = models.CharField(max_length=80)
	value = models.FloatField(default=0)
	game = models.ForeignKey('Game', related_name='cotations')	
	winning = models.BooleanField(default=False)
	is_standard = models.BooleanField(default=False)
	kind = models.CharField(max_length=100)
	handicap = models.FloatField(blank = True, null = True)
	total = models.FloatField(blank = True, null = True)
	objects = GamesManager()
	
	@staticmethod
	def consuming_api():
		from utils.utils import renaming_cotations

		for game in Game.objects.all():
			r = requests.get("https://soccer.sportmonks.com/api/v2.0/odds/fixture/"+str(game.pk)+"/bookmaker/2?api_token="+TOKEN)			
			game.cotations.all().delete()							
			for kind in r.json().get('data'):
				kind_name = kind['name']				
				for cotation in kind['bookmaker']['data'][0]['odds']['data']:
					if kind_name != 'Asian Handicap' and kind_name != 'Handicap Result' and kind_name != 'Handicap' and kind_name != '3Way Handicap':
						if kind_name == '3Way Result':
							c = Cotation(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']),value=cotation['value'],game=game, is_standard = True,
								handicap=cotation['handicap'], total=cotation['total'])
							if kind_name in MARKET_NAME.keys():
								c.kind = MARKET_NAME[kind_name]
								c.save()
							else:
								c.kind = kind_name
								c.save()

						else:
							c = Cotation(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']),value=cotation['value'],game=game, is_standard = False,
								handicap=cotation['handicap'], total=cotation['total'])
							if kind_name in MARKET_NAME.keys():
								c.kind = MARKET_NAME[kind_name]
								c.save()
							else:
								c.kind = kind_name
								c.save()


	class Meta:
		verbose_name = 'Cota'
		verbose_name_plural = 'Cotas'

	def __str__(self):
		return str(self.value)


class Payment(models.Model):
	who_set_payment = models.ForeignKey('user.Seller', null=True)
	status_payment = models.CharField(max_length=80, choices=PAYMENT_STATUS, default=PAYMENT_STATUS[0][1])
	payment_date = models.DateTimeField(null=True, auto_now=True)

	class Meta:
		verbose_name = 'Pagamento'
		verbose_name_plural = 'Pagamentos'

