from django.db import models
# Create your models here.

BET_TICKET_STATUS = (
		('WAITING_RESULT', 'waiting result'),
		('NOT_WON', 'not won'),
		('WON', 'won'),
	)

COTATION_STATUS = (
        ('OPEN', 'open'),
        ('HAPPENING', 'happening'),
        ('NOT_HAPPENING', 'not_happening'),        
    )

GAME_STATUS = (
        ('FINISHED', 'finished'),
        ('HAPPENING', 'happening'),
        ('NOT_HAPPENING', 'not_happening'),        
    )

PAYMENT_STATUS = (
		('PAID', 'paid'),
		('NOT_PAID', 'not_paid'),
	)
		
class Bet(models.Model):
	bet_ticket = models.ForeignKey('BetTicket',related_name='my_bets')
	cotation = models.ForeignKey('Cotation',related_name='my_bets')

	@property
	def user(self):
		return self.bet_ticket.punter.first_name


class BetTicket(models.Model):	
	punter = models.ForeignKey('user.Punter', related_name='my_bet_tickets')
	seller = models.ForeignKey('user.Seller', related_name='bet_tickets_validated_by_me')
	creation_date = models.DateTimeField(null=True)
	payment = models.OneToOneField('Payment')
	reward = models.ForeignKey('Reward')
	value = models.DecimalField(max_digits=4, decimal_places=2)
	bet_ticket_status = models.CharField(max_length=45, choices=BET_TICKET_STATUS)


class Game(models.Model):
	name = models.CharField(max_length=45)	
	start_game_date = models.DateTimeField(null=True)
	championship = models.ForeignKey('Championship',related_name='my_games')
	status_game = models.CharField(max_length=45,default='not happening', choices=GAME_STATUS)


class Championship(models.Model):
	name = models.CharField(max_length=45)


class Reward(models.Model):
	who_rewarded = models.ForeignKey('user.Seller')
	value = models.DecimalField(max_digits=4, decimal_places=2)
	reward_date = models.DateTimeField(null=True)


class Cotation(models.Model):
	name = models.CharField(max_length=25)
	value = models.DecimalField(max_digits=4, decimal_places=2)
	bet = models.ForeignKey('Bet',related_name='cotations')
	game = models.ForeignKey('Game',related_name='cotations')
	status = models.CharField(max_length=25, choices=COTATION_STATUS)


class Payment(models.Model):
	status = models.CharField(max_length=25, choices=PAYMENT_STATUS)
	who_set_payment = models.ForeignKey('user.Seller')
	payment_date = models.DateTimeField(null=True)
