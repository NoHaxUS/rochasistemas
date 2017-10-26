from django.db import models
# Create your models here.

BET_TICKET_STATUS = (
		('WAITING_RESULT', 'waiting result'),
		('NOT_WON', 'not won'),
		('WON', 'won'),
	)

COTATION_STATUS = (
        ('OPEN', 'open'),
        ('HAPPEN', 'happen'),
        ('NOT_HAPPEN', 'not_happen'),        
    )

PAYMENT_STATUS = (
		('PAID', 'paid'),
		('NOT_PAID', 'not_paid'),
	)
		
class Bet(models.Model):	
	#user = models.ForeignKey('') it's gonna be a property
	game = models.ForeignKey('Game',related_name='my_bets')


class BetTicket(models.Model):	
	seller = models.ForeignKey('user.Seller', related_name='bet_tickets_validated_by_me')
	punter = models.ForeignKey('user.Punter', related_name='my_bet_tickets')
	creation_date = models.DateTimeField(null=True)
	payment = models.OneToOneField('Payment')
	reward = models.ForeignKey('Reward')
	#bet_value = SEARCH FOR A TYPE MONEY APP
	bet_ticket_status = models.CharField(max_length=45, choices=BET_TICKET_STATUS)

class Game(models.Model):
	name = models.CharField(max_length=45)	
	start_game_date = models.DateTimeField(null=True)
	championship = models.CharField(max_length=25)
	visible = models.BooleanField(default=False)


class Reward(models.Model):
	who_rewarded = models.ForeignKey('user.Seller')
	#value = SEARCH FOR A TYPE MONEY APP
	reward_date = models.DateTimeField(null=True)


class Cotation(models.Model):
	name = models.CharField(max_length=25)
	#value = SEARCH FOR A TYPE MONEY APP
	bet = models.ForeignKey('Bet',related_name='cotations')
	game = models.ForeignKey('Game',related_name='cotations')
	status = models.CharField(max_length=25, choices=COTATION_STATUS)


class Payment(models.Model):
	status = models.CharField(max_length=25, choices=PAYMENT_STATUS)
	who_set_payment = models.ForeignKey('user.Seller')
	payment_date = models.DateTimeField(null=True)
