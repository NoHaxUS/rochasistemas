from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from .manager import GamesManager,CotationsManager
from user.models import Seller
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
import requests
import decimal
from django.conf import settings
# Create your models here.

TOKEN='OOabOgBw4awrsYQ51DIWz3i4ILKWxBAXqLQI5b01xzZuoKhyBHCcdINUbIeM'

BET_TICKET_STATUS = (
		('Aguardando Resultados', 'Aguardando Resultados'),
		('Não Venceu', 'Não Venceu'),
		('Venceu', 'Venceu'),
	)

REWARD_STATUS = (
		('Aguardando Resultados', 'Aguardando Resultados'),
		('O apostador foi pago', 'O apostador foi pago'),
		('Esse ticket não venceu', 'Esse ticket não venceu'),
		('Venceu, Aguardando pagamento', 'Venceu, Aguardando pagamento'),
	)

GAME_STATUS = (
		('NS', 'Não Iniciado'),
		('LIVE','Ao Vivo'),
		('HT', 'Meio Tempo'),
		('FT', 'Tempo Total')	,	
		('ET', 'Tempo Extra'),
		('PEN_LIVE', 'Penaltis'),
		('AET', 'Terminou após tempo extra'),
		('BREAK', 'Esperando tempo extra'),
		('FT_PEN', 'Tempo total após os penaltis'),
		('CANCL', 'Cancelado'),
		('POSTP', 'Adiado'),
		('INT', 'Interrompindo'),
		('ABAN', 'Abandonado'),
		('SUSP', 'Suspendido'),
		('AWARDED', 'Premiado'),
		('DELAYED', 'Atrasado'),
		('TBA', 'A ser anunciado'),
		('WO', 'WO'),
	)


PAYMENT_STATUS = (
		('Aguardando Pagamento do Ticket', 'Aguardando Pagamento do Ticket'),
		('Pago', 'Pago'),
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
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_bet_tickets')
	seller = models.ForeignKey('user.Seller', null=True, related_name='bet_tickets_validated_by_me')
	cotations = models.ManyToManyField('Cotation', related_name='bet_ticket')
	creation_date = models.DateTimeField(auto_now_add=True)	
	reward = models.ForeignKey('Reward', null=True)
	payment = models.OneToOneField('Payment', null=True)
	value = models.FloatField()
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

	def update_ticket_status(self):
		not_winning = False
		if self.check_ticket_status:			
			for c in self.cotations.all():
				if c.winning is not None:
					if not c.winning:
						self.bet_ticket_status = BET_TICKET_STATUS[1][1]
						self.save()
						not_winning = True
						return 'Status do ticket atualizado com sucesso. You Lost'
				else:
					self.bet_ticket_status = BET_TICKET_STATUS[0][1]
					self.save()
					return 'Ticket aguardando resultado'
			
			if not not_winning:
				self.bet_ticket_status = BET_TICKET_STATUS[2][1]
				self.save()
				return 'Status do ticket atualizado com sucesso. You Won'
		else:
			self.bet_ticket_status = BET_TICKET_STATUS[0][1]
			self.save()
			return 'Ticket aguardando resultado'
		
			

	def check_ticket_status(self):
		ticket_finished = True

		for c in self.cotations.all():
			if not c.game.odds_calculated:
				ticket_finished = False

		return ticket_finished

	@staticmethod
	def processing_tickets():
		for ticket in BetTicket.objects.all():
			ticket.update_ticket_status()


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
	odds_calculated = models.BooleanField()
	visitor_team_score = models.IntegerField(blank = True, null = True)
	local_team_score = models.IntegerField(blank = True, null = True)
	ht_score = models.CharField(max_length=80, null=True)
	ft_score = models.CharField(max_length=80, null=True)	
	objects = GamesManager()
	
	@staticmethod
	def consuming_api(first_date, second_date):

		url_request = "https://soccer.sportmonks.com/api/v2.0/fixtures/between/"+first_date+"/"+second_date+"?api_token="+TOKEN+"&include=localTeam,visitorTeam&tz=America/Sao_Paulo"
		r = requests.get(url_request)

		for i in range(1, r.json().get('meta')['pagination']['total_pages']):			

			for game in r.json().get('data'):					
				if Championship(pk = game['league_id']) in Championship.objects.all():
					if Game(pk = game["id"]) in Game.objects.all():
						g = Game.objects.get(pk = game['id'])
						g.status_game = game['time']['status']
						g.local_team_score=game['scores']['localteam_score']
						g.visitor_team_score=game['scores']['visitorteam_score']
						g.ht_score=game['scores']['ht_score']
						g.ft_score=game['scores']['ft_score']
						g.odds_calculated=game['winning_odds_calculated']
						g.save()
						
					else:
						Game(pk=game['id'],
							start_game_date=datetime.strptime(game["time"]["starting_at"]["date_time"], "%Y-%m-%d %H:%M:%S"),
							name=game['localTeam']['data']['name']+" x " +game['visitorTeam']['data']['name'], 
							championship=Championship.objects.get(pk=game["league_id"]), status_game=game['time']["status"],
							local_team_score=game['scores']['localteam_score'], visitor_team_score=game['scores']['visitorteam_score'],
							ht_score=game['scores']['ht_score'],ft_score=game['scores']['ft_score'],
							odds_calculated=game['winning_odds_calculated']).save() 

			r = requests.get("https://soccer.sportmonks.com/api/v2.0/fixtures/between/"+first_date+"/"+second_date+"?page="+str((i+1))+"&api_token="+TOKEN+"&include=localTeam,visitorTeam&tz=America/Sao_Paulo")
	
	def is_able(self):
		if self.odds_calculated:
			if self.visitor_team_score is not None and self.local_team_score is not None and self.ht_score is not None and self.ft_score is not None and self.cotations.count() > 0:
				if len(self.ht_score) >= 3 and len(self.ft_score) >= 3:
					return True

		return False

	class Meta:
		verbose_name = 'Jogo'
		verbose_name_plural = 'Jogos'

	def __str__(self):
		return self.name	


class Championship(models.Model):
	name = models.CharField(max_length=80)
	country = models.CharField(max_length=45)

	@staticmethod
	def consuming_api():
		r = requests.get("https://soccer.sportmonks.com/api/v2.0/leagues/?api_token="+TOKEN + "&include=country&tz=America/Sao_Paulo")
		
		for championship in r.json().get('data'):
			Championship(pk=championship['id'],name = championship['name'],country = championship['country']['data']['name']).save()			

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Campeonato'
		verbose_name_plural = 'Campeonatos'



class Reward(models.Model):
	who_rewarded = models.ForeignKey('user.Seller', null=True)
	reward_date = models.DateTimeField(null=True, auto_now=True)
	value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	status_reward = models.CharField(max_length=80, choices=REWARD_STATUS, default=REWARD_STATUS[0][1])

	def __str__(self):
		return str(self.value)

	class Meta:
		verbose_name = 'Recompensa'
		verbose_name_plural = 'Recompensas'


class Cotation(models.Model):
	name = models.CharField(max_length=80)
	value = models.FloatField(default=0)
	game = models.ForeignKey('Game', related_name='cotations')	
	winning = models.NullBooleanField()
	is_standard = models.BooleanField(default=False)
	kind = models.CharField(max_length=100)
	handicap = models.FloatField(blank = True, null = True)
	total = models.FloatField(blank = True, null = True)
	objects = GamesManager()	

	
	@staticmethod
	def consuming_api():
		from utils.utils import renaming_cotations

		for game in Game.objects.all():
			r = requests.get("https://soccer.sportmonks.com/api/v2.0/odds/fixture/"+str(game.pk)+"/bookmaker/2?api_token="+TOKEN+"&tz=America/Sao_Paulo")			
			# r = requests.get("http://localhost:8000/utils/test_url/")							
			for kind in r.json().get('data'):
				kind_name = kind['name']				
				for cotation in kind['bookmaker']['data'][0]['odds']['data']:
					if kind_name != 'Asian Handicap' and kind_name != 'Handicap Result' and kind_name != 'Handicap' and kind_name != '3Way Handicap' and kind_name != 'Corners Over Under':
						if kind_name == '3Way Result':
							cotations = game.cotations.all().filter(kind=MARKET_NAME.setdefault(kind_name,kind_name))
							if cotations.filter(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip()).exists():
								c = cotations.filter(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip())
								c.update(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip(),value=cotation['value'],game=game, is_standard = True,
									handicap=cotation['handicap'], total=cotation['total'], winning=cotation['winning'],kind=MARKET_NAME.setdefault(kind_name,kind_name))
							else:
								Cotation(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip(),value=cotation['value'],game=game, is_standard = True,
									handicap=cotation['handicap'], total=cotation['total'], winning=cotation['winning'],kind=MARKET_NAME.setdefault(kind_name,kind_name)).save()
								
						else:

							if kind_name == 'Result/Total Goals':
								cotations = game.cotations.all().filter(kind=MARKET_NAME.setdefault(kind_name,kind_name))
								if cotations.filter(name=renaming_cotations(cotation['label']," ").strip()).exists():
									c = cotations.filter(name=renaming_cotations(cotation['label']," ").strip())
									c.update(name=renaming_cotations(cotation['label']," ").strip(),value=cotation['value'],game=game, is_standard = False,
										handicap=cotation['handicap'], total=cotation['total'], winning=cotation['winning'],kind=MARKET_NAME.setdefault(kind_name,kind_name))
								else:									
									Cotation(name=renaming_cotations(cotation['label']," ").strip(),value=cotation['value'],game=game, is_standard = False,
										handicap=cotation['handicap'], total=cotation['total'], winning=cotation['winning'],kind=MARKET_NAME.setdefault(kind_name,kind_name)).save()

									
							else:									
								cotations = game.cotations.all().filter(kind=MARKET_NAME.setdefault(kind_name,kind_name))
								if cotations.filter(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip()).exists():
									c = cotations.filter(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip())
									c.update(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip(),value=cotation['value'],game=game, is_standard = False,
										handicap=cotation['handicap'], total=cotation['total'], winning=cotation['winning'],kind=MARKET_NAME.setdefault(kind_name,kind_name))
								else:
									Cotation(name=renaming_cotations(cotation['label']," " if cotation['total'] == None else cotation['total']).strip(),value=cotation['value'],game=game, is_standard = False,
										handicap=cotation['handicap'], total=cotation['total'], winning=cotation['winning'],kind=MARKET_NAME.setdefault(kind_name,kind_name)).save()
									

	@staticmethod
	def processing_cotations():
		for game in Game.objects.all().filter(status_game='FT'):			
			print(game.pk, game.name)
			#dento do if só entra games q tenham os dados do score ok
			try:
				if game.is_able():							
					#nesse conjunto de if,elif e else são processados 4 markets			
					#Vencedor do Encontro, Casa/Visitante, Dupla Chance,Vencedor Não tomará Gol(s) 		
					cotations = game.cotations.all().filter(kind='Vencedor do Encontro') 
					if game.visitor_team_score > game.local_team_score:					
						cotations.update(winning=False)									
						c2 = cotations.filter(name='2')					
						c2.update(winning= True)					
						cotations = game.cotations.all().filter(kind='Casa/Visitante')
						cotations.filter(name='1').update(winning=False)
						cotations.filter(name='2').update(winning=True)					
						if game.cotations.all().filter(kind='Dupla Chance').count()>0:
							cotations = game.cotations.all().filter(kind='Dupla Chance')
							cotations.update(winning=True)					
							cotations.filter(name='Casa/Empate').update(winning=False)
							

						if game.cotations.all().filter(kind='Vencedor Não tomará Gol(s)').count()>0:
							cotations = game.cotations.all().filter(kind='Vencedor Não tomará Gol(s)')
							cotations.update(winning=True)
							if game.local_team_score > 0:
								cotations.filter(name='2').update(winning=True)							


					elif game.visitor_team_score < game.local_team_score:
						cotations.update(winning=False)
						cotations.filter(name='1').update(winning=True)					
						cotations = game.cotations.all().filter(kind='Casa/Visitante')
						cotations.filter(name='1').update(winning=True)
						cotations.filter(name='2').update(winning=False)
						
						if game.cotations.all().filter(kind='Dupla Chance').count()>0:
							cotations = game.cotations.all().filter(kind='Dupla Chance')					
							cotations.update(winning=True)
							cotations.filter(name='Empate/Visitante').update(winning=False)						

						if game.cotations.all().filter(kind='Vencedor Não tomará Gol(s)').count()>0:
							cotations = game.cotations.all().filter(kind='Vencedor Não tomará Gol(s)')
							cotations.update(winning=True)
							if game.visitor_team_score > 0:
								cotations.filter(name='1').update(winning=True)							

					else:
						cotations.update(winning=False)					
						cotations.filter(name='X').update(winning=True)															
						cotations = game.cotations.all().filter(kind='Casa/Visitante')
						cotations.filter(name='1').update(winning=False)
						cotations.filter(name='2').update(winning=False)									
						if game.cotations.all().filter(kind='Dupla Chance').count()>0:
							cotations = game.cotations.all().filter(kind='Dupla Chance')
							cotations.update(winning=True)
							c = cotations.filter(name='Casa/Visitante').update(winning=False)
							
					#dentro desse if é tradado o market Etapa com Mais Gol(s)
					if game.cotations.all().filter(kind='Etapa com Mais Gol(s)').count()>0:
						cotations = game.cotations.all().filter(kind='Etapa com Mais Gol(s)')
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
					if game.cotations.all().filter(kind='Vencedor nas Duas Etapas').count()>0:
						result_1_etapa = int(game.ht_score.split('-')[0]) - int(game.ht_score.split('-')[1])
						result_2_etapa = int(game.ft_score.split('-')[0]) - int(game.ft_score.split('-')[1])
						cotations = game.cotations.all().filter(kind='Vencedor nas Duas Etapas')
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
					if game.cotations.all().filter(kind='Número Exato de Gol(s)').count()>0:
						result = int(game.ft_score.split('-')[0]) + int(game.ft_score.split('-')[1])
						cotations = game.cotations.all().filter(kind='Número Exato de Gol(s)')
						
						if result >= 7:
							cotations.update(winning=False)
							cotations.filter(name='more 7').update(winning=True)

						else:
							cotations.update(winning=False)
							cotations.filter(name=str(result)).update(winning=True)
							

					#dentro desse if é tradado o market Intervalo/Final de Jogo
					if game.cotations.all().filter(kind='Intervalo/Final de Jogo').count()>0:
						result_1_etapa = int(game.ht_score.split('-')[0]) - int(game.ht_score.split('-')[1])
						result_2_etapa = int(game.ft_score.split('-')[0]) - int(game.ft_score.split('-')[1])
						cotations = game.cotations.all().filter(kind='Intervalo/Final de Jogo')
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
					if game.cotations.all().filter(kind='Resultado/2 Times Marcam').count()>0:
						cotations = game.cotations.all().filter(kind='Resultado/2 Times Marcam')
						result = int(game.ft_score.split('-')[0]) - int(game.ft_score.split('-')[1])
						if result > 0:
							if game.local_team_score > 0 and game.visitor_team_score > 0:						
								cotations.update(winning=False)
								cotations.filter(name="Casa/Sim").update(winning=True)							

							else:
								cotations.update(winning=False)
								cotations.filter(name="Casa/Não").update(winning=True)
								
							
							if game.cotations.all().filter(kind="Resultado/Total de Gol(s)").count()>0:
									cotations = game.cotations.all().filter(kind="Resultado/Total de Gol(s)")			
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

							if game.cotations.all().filter(kind="Resultado/Total de Gol(s)").count()>0:
									cotations = game.cotations.all().filter(kind="Resultado/Total de Gol(s)")			
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
								
							if game.cotations.all().filter(kind="Resultado/Total de Gol(s)").count()>0:
									cotations = game.cotations.all().filter(kind="Resultado/Total de Gol(s)")			
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

