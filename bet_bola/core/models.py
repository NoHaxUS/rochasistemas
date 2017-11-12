from django.db import models
from django.core.exceptions import ValidationError
import decimal
# Create your models here.

BET_TICKET_STATUS = (
		('WAITING_RESULT', 'waiting result'),
		('NOT_WON', 'not won'),
		('WON', 'won'),
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

COTATION_STATUS = (
		('NOT_HAPPENING', 'not_happening'),        
        ('HAPPENING', 'happening'),
        ('OPEN', 'open'),        
    )

PAYMENT_STATUS = (
		('PAID', 'paid'),
		('NOT_PAID', 'not_paid'),
	)
		

class BetTicket(models.Model):	
	punter = models.ForeignKey('user.Punter', related_name='my_bet_tickets')
	seller = models.ForeignKey('user.Seller', blank=True, null=True, related_name='bet_tickets_validated_by_me')
	cotations = models.ManyToManyField('Cotation', related_name='my_bet_tickets')
	creation_date = models.DateTimeField(blank=True)	
	reward = models.ForeignKey('Reward',blank=True, null=True)
	value = models.DecimalField(max_digits=4, decimal_places=2, null=True)
	bet_ticket_status = models.CharField(max_length=45, choices=BET_TICKET_STATUS,default=BET_TICKET_STATUS[0])
	payment = models.OneToOneField('Payment', blank=True, null=True)

	def __str__(self):
		return str(self.pk)

class Game(models.Model):
	name = models.CharField(max_length=45)	
	start_game_date = models.DateTimeField(null=True)
	championship = models.ForeignKey('Championship',related_name='my_games')
	status_game = models.CharField(max_length=45,default=GAME_STATUS[0], choices=GAME_STATUS)

	def __str__(self):
		return self.name	


class Championship(models.Model):
	name = models.CharField(max_length=45)

	def __str__(self):
		return self.name


class Reward(models.Model):
	who_rewarded = models.ForeignKey('user.Seller')	
	reward_date = models.DateTimeField(null=True)
	value_max = models.DecimalField(max_digits=6, decimal_places=1,default=10000.0)
	value = models.DecimalField(max_digits=6, decimal_places=1,)

	def clean(self):        
		if self.value_max < self.value:
			raise ValidationError('Valor excede o valor maximo')


class Cotation(models.Model):	
	value = models.DecimalField(max_digits=4, decimal_places=2)	
	game = models.ForeignKey('Game',related_name='cotations')
	status = models.CharField(max_length=25, choices=COTATION_STATUS)

	def __str__(self):
		return str(self.value)


class Payment(models.Model):
	status = models.CharField(max_length=25, choices=PAYMENT_STATUS)
	who_set_payment = models.ForeignKey('user.Seller')
	payment_date = models.DateTimeField(null=True)	
