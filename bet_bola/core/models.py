from django.db import models
# Create your models here.

BET_TICKET_STATUS = (
		('WAITING_RESULT', 'waiting result'),
		('NOT_WON', 'not won'),
		('WON', 'won'),
	)

COTATION_STATUS = (
        ('HOME', 'open'),
        ('TIE', 'tie'),
        ('AWAY', 'away'),        
    )

GAME_STATUS = (
		('NOT_HAPPENING', 'not_happening'),        
        ('HAPPENING', 'happening'),
        ('FINISHED', 'finished'),        
    )

PAYMENT_STATUS = (
		('PAID', 'paid'),
		('NOT_PAID', 'not_paid'),
	)
		

class BetTicket(models.Model):	
	punter = models.ForeignKey('user.Punter', related_name='my_bet_tickets')
	seller = models.ForeignKey('user.Seller', related_name='bet_tickets_validated_by_me')
	cotations = models.ManyToManyField('Cotation', related_name='my_bet_tickets')
	creation_date = models.DateTimeField(blank=True)	
	reward = models.ForeignKey('Reward',blank=True, null=True)
	value = models.DecimalField(max_digits=4, decimal_places=2, null=True)
	bet_ticket_status = models.CharField(max_length=45, choices=BET_TICKET_STATUS,default=BET_TICKET_STATUS[0])

	def __str__(self):
		return self.punter.first_name

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
	value = models.DecimalField(max_digits=4, decimal_places=2)
	reward_date = models.DateTimeField(null=True)


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
	bet_ticket = models.OneToOneField('BetTicket')
