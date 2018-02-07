from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from .manager import GamesManager,CotationsManager
from user.models import Seller
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
import decimal
from django.conf import settings
import utils.timezone as tzlocal



# Create your models here.


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

class BetTicket(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_bet_tickets', on_delete=models.PROTECT, verbose_name='Apostador')
	random_user = models.ForeignKey('user.RandomUser',null=True, on_delete=models.SET_NULL, verbose_name='Cliente')
	cotations = models.ManyToManyField('Cotation', related_name='bet_ticket', verbose_name='Cota')
	creation_date = models.DateTimeField(verbose_name='Data da aposta')	
	reward = models.ForeignKey('Reward', null=True,on_delete=models.PROTECT, verbose_name='Recompensa')
	payment = models.OneToOneField('Payment', null=True,on_delete=models.PROTECT, verbose_name='Pagamento')
	value = models.FloatField(verbose_name='Apostado')
	bet_ticket_status = models.CharField(max_length=80, choices=BET_TICKET_STATUS,default=BET_TICKET_STATUS[0][1],verbose_name='Status')


	def ticket_valid(self, user):
		self.payment.status_payment = PAYMENT_STATUS[1][1]
		self.payment.payment_date = tzlocal.now()
		self.payment.who_set_payment = Seller.objects.get(pk=user.pk)
		self.payment.save()

	def reward_payment(self, user):
		self.reward.status_reward = REWARD_STATUS[1][1]
		self.reward.reward_date = tzlocal.now()
		self.reward.who_rewarded = Seller.objects.get(pk=user.pk)
		self.reward.save()

	def cota_total(self):
		cota_total = 1
		
		for cotation in self.cotations.all():
			cota_total *= cotation.value
		
		return round(cota_total,2)

	def update_ticket_status(self):
		not_winning = False
		if self.check_ticket_status:			
			for c in self.cotations.all():
				if c.winning is not None:
					if not c.winning:
						self.bet_ticket_status = BET_TICKET_STATUS[1][1]
						self.save()
						not_winning = True
						return 'Status do ticket atualizado com sucesso. Perdeu'
				else:
					self.bet_ticket_status = BET_TICKET_STATUS[0][1]
					self.save()
					return 'Ticket aguardando resultado'
			
			if not not_winning:
				self.bet_ticket_status = BET_TICKET_STATUS[2][1]
				self.save()
				return 'Status do ticket atualizado com sucesso. Ganhou'
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
	name = models.CharField(max_length=80, verbose_name='Nome do Jogo')	
	start_game_date = models.DateTimeField(verbose_name='Início da Partida')
	championship = models.ForeignKey('Championship',related_name='my_games', on_delete=models.CASCADE,verbose_name='Campeonato')
	status_game = models.CharField(max_length=80,default=GAME_STATUS[0][1], choices=GAME_STATUS,verbose_name='Status do Jogo')
	odds_calculated = models.BooleanField()
	local_team_score = models.IntegerField(blank = True, null = True, verbose_name='Placar Time de Casa')
	visitor_team_score = models.IntegerField(blank = True, null = True, verbose_name='Placar do Visitante')
	ht_score = models.CharField(max_length=80, null=True, verbose_name='Placar até o meio-tempo')
	ft_score = models.CharField(max_length=80, null=True, verbose_name='Placar no final do Jogo', help_text="Placar final Ex: 3-5 (Casa-Visita)")
	odds_processed = models.BooleanField(default=False)

	objects = GamesManager()
	
	
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
	name = models.CharField(max_length=80, verbose_name='Nome', help_text='Campeonato')
	country = models.CharField(max_length=45, verbose_name='País')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Campeonato'
		verbose_name_plural = 'Campeonatos'



class Reward(models.Model):
	who_rewarded = models.ForeignKey('user.Seller', null=True, on_delete=models.PROTECT)
	reward_date = models.DateTimeField(null=True)
	value = models.FloatField(default=0)
	status_reward = models.CharField(max_length=80, choices=REWARD_STATUS, default=REWARD_STATUS[0][1])

	def __str__(self):
		return str(self.value)

	class Meta:
		verbose_name = 'Recompensa'
		verbose_name_plural = 'Recompensas'


class Cotation(models.Model):
	name = models.CharField(max_length=80, verbose_name='Nome da Cota')
	original_value = models.FloatField(default=0,verbose_name='Valor Original')
	value = models.FloatField(default=0, verbose_name='Valor Modificado')
	game = models.ForeignKey('Game', related_name='cotations', on_delete=models.CASCADE, verbose_name='Jogo')	
	winning = models.NullBooleanField(verbose_name='Vencedor ?')
	is_standard = models.BooleanField(default=False, verbose_name='Cota Padrão ?')
	kind = models.CharField(max_length=100, verbose_name='Tipo')
	total = models.FloatField(blank = True, null = True)
	objects = GamesManager()


	def save(self):
		if not Cotation.objects.filter(name=self.name, kind=self.kind, game=self.game).exists():
			super().save()
					


	class Meta:
		verbose_name = 'Cota'
		verbose_name_plural = 'Cotas'

	def __str__(self):
		return str(self.value)


class Payment(models.Model):
	who_set_payment = models.ForeignKey('user.Seller', null=True, on_delete=models.PROTECT)
	status_payment = models.CharField(max_length=80, choices=PAYMENT_STATUS, default=PAYMENT_STATUS[0][1])
	payment_date = models.DateTimeField(null=True)
	seller_was_rewarded = models.BooleanField(default=False)


	def __str__(self):
		return self.status_payment



	class Meta:
		verbose_name = 'Pagamento'
		verbose_name_plural = 'Pagamentos'

