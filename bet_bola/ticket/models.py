from django.db import models
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import utils.timezone as tzlocal
from django.utils import timezone
import utils.timezone as tzlocal
from user.models import TicketOwner, Seller, Punter
from ticket.logic.reward import get_reward_value
from ticket.logic import ticket
from decimal import Decimal

class Ticket(models.Model):

    TICKET_STATUS = (
        (0, 'Aguardando Resultados'),
        (1, 'Não Venceu'),
        (2, 'Venceu, Ganhador Pago'),
        (3, 'Venceu, Bilhete não Pago'),
        (4, 'Venceu, Prestar Contas'),
        (5, 'Cancelado'),
        (6, 'Reebolsado')
    )
    
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    ticket_id = models.CharField(max_length=10, verbose_name="Ticket ID")
    owner = models.ForeignKey('user.TicketOwner', on_delete=models.CASCADE, verbose_name='Dono do Bilhete')
    cotations = models.ManyToManyField('core.Cotation', related_name='ticket', verbose_name='Cotas')
    creation_date = models.DateTimeField(verbose_name='Data da Aposta', default=tzlocal.now)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_created_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Criado por')
    reward = models.OneToOneField('Reward', related_name='ticket', on_delete=models.CASCADE, verbose_name='Prêmio')
    payment = models.OneToOneField('Payment', related_name='ticket', on_delete=models.CASCADE, verbose_name='Pagamento')
    bet_value = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Valor Apostado')
    status = models.IntegerField(default=0, choices=TICKET_STATUS, verbose_name='Status do Ticket')
    closed_in_for_seller = models.BooleanField(default=False, verbose_name='Entrada Vendedor Caixa')
    closed_in_for_manager = models.BooleanField(default=False, verbose_name='Entrada Gerente Caixa')
    closed_out_for_seller = models.BooleanField(default=False, verbose_name='Saída Vendedor Caixa')
    closed_out_for_manager = models.BooleanField(default=False, verbose_name='Saída Gerente Caixa')
    store = models.ForeignKey('core.Store', related_name='my_tickets', verbose_name='Banca', on_delete=models.CASCADE)
    available = models.BooleanField(default=True, verbose_name='Disponível?')
    
    def won_bonus(self):
        if self.status in [2,4] and self.store.my_configuration.bonus_won_ticket:
            return round(Decimal(self.reward.value * self.store.my_configuration.bonus_by_won_ticket / 100),2)                
        return round(Decimal(0),2)

    def update_ticket_reward(self):
        
        raw_reward_value = self.cotation_sum() * self.bet_value
        self.reward.value = get_reward_value(self.bet_value, raw_reward_value, self.store)[1]
        self.reward.save()


    def toggle_availability(self):
        self.available = not self.available
        self.save()

    def cancel_ticket(self, user):
        return ticket.cancel_ticket(self, user)

    def validate_ticket(self, user):
        return ticket.validate_ticket(self, user)

    def reward_winner(self, user):
        return ticket.reward_winner(self, user)

    def cotation_sum(self):
        return ticket.cotation_sum(self)

    def __str__(self):
        return str(self.ticket_id)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'        
        permissions = (
            ('can_validate_payment', "Can validate user ticket"),
            ('can_reward', "Can reward a user"),
        )


class Reward(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_rewarded_the_winner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    value = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Valor da Recompensa')
    date = models.DateTimeField(null=True, blank=True, verbose_name='Data de Pagamento do Prêmio')

    def __str__(self):
        return str(self.value)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'



class Payment(models.Model):

    PAYMENT_STATUS = (
        (0, 'Aguardando Pagamento'),
        (1, 'Pagamento em Análise'),
        (2, 'Pago'),
        (3, 'Pagamento Cancelado'),
        (4, 'Pagamento Recusado pelo Cartão'),
        (5, 'Pagamento Reembolsado')
    )


    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_paid = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cambista')
    status = models.IntegerField(choices=PAYMENT_STATUS, default=0, verbose_name='Status do Pagamento')
    date = models.DateTimeField(null=True, blank=True, verbose_name='Data do Pagamento')

    def __str__(self):
        return self.get_status_display()

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'


