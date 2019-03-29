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
from user.models import NormalUser, Seller, Punter


class Ticket(models.Model):

    TICKET_STATUS = {
        'Aguardando Resultados':'Aguardando Resultados',
        'Não Venceu': 'Não Venceu',
        'Venceu':'Venceu',
        'Venceu, não pago' : 'Venceu, não pago',
        'Cancelado' : 'Cancelado'
    }
    
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Apostador')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_created_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cambista')
    normal_user = models.ForeignKey(NormalUser, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cliente')
    cotations = models.ManyToManyField('core.Cotation', related_name='ticket', verbose_name='Cota')
    creation_date = models.DateTimeField(verbose_name='Data da Aposta')
    reward = models.OneToOneField('Reward', related_name='ticket', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Recompensa')
    payment = models.OneToOneField('Payment', related_name='ticket', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Pagamento')
    value = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Valor Apostado')    
    visible = models.BooleanField(default=True, verbose_name='Visível?')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

        ('Aguardando Resultados', 'Aguardando Resultados'),
        ('O apostador foi pago', 'O apostador foi pago'),
        ('Esse ticket não venceu', 'Esse ticket não venceu'),
        ('Venceu, Pagar Apostador', 'Venceu, Pagar Apostador'),
        ('Venceu, não pago','Venceu, não pago')

    @property
    def ticket_status(self):
        if self.payment.status_payment == Payment.PAYMENT_STATUS[2][1]:
            return Payment.PAYMENT_STATUS[2][1]

        if self.cotations.filter(settlement__in=[1,3,4]).exclude(game__game_status__in = (4,5,6,7,8)).count() > 0:
            return Ticket.TICKET_STATUS['Não Venceu']

        if self.cotations.filter(settlement__isnull=True).exclude(game__game_status__in = (4,5,6,7,8)).count() > 0:
            return Ticket.TICKET_STATUS['Aguardando Resultados']

        if not self.cotations.filter(settlement__in=[1,3,4]).exclude(game__game_status__in = (4,5,6,7,8)).count() > 0 and self.cotations.exclude(game__game_status__in = (4,5,6,7,8)).exclude(settlement=-1).count() > 0 and self.payment.status_payment == 'Pago':
            return Ticket.TICKET_STATUS["Venceu"]
        
        if not self.cotations.filter(settlement__in=[1,3,4]).exclude(game__game_status__in = (4,5,6,7,8)).count() > 0 and self.cotations.exclude(game__game_status__in = (4,5,6,7,8)).exclude(settlement=-1).count() > 0 and self.payment.status_payment == Payment.PAYMENT_STATUS[0][1]:
            return Ticket.TICKET_STATUS["Venceu, não pago"]
        
        return "Bilhete Anulado"


    def get_punter_name(self):
        if self.user:
            return self.user.first_name
        elif self.normal_user:
            return self.normal_user.first_name
    get_punter_name.short_description = 'Apostador'


    def hide_ticket(self):
        self.visible = False
        self.save()
        return {"message" :"Jogo "+ str(self.pk) +" Ocultado."}


    def show_ticket(self):
        self.visible = True
        self.save()
        return {"message" :"Jogo "+ str(self.pk) +" Exibido."}


    def get_ticket_link(self):
        from django.utils.safestring import mark_safe
        link = '<a href="/ticket/'+str(self.pk) + '/" class="consult">Consultar<a/>'
        return mark_safe(link)
    get_ticket_link.short_description = 'Ver'


    def seller_related(self):
        if self.payment:
            return self.payment.who_set_payment
    seller_related.short_description = 'Cambista'


    def cancel_ticket(self, user):
        from history.models import TicketCancelationHistory
        from core.models import Store

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        who_cancelled  = str(user.pk) + ' - ' + user.username
        if not self.ticket_status == Ticket.TICKET_STATUS['Aguardando Resultados']:
            return {'success':False,
                'message':' Ticket '+ str(self.pk)+ ' não cancelado, pois não está aguardando resultados.'}
        
        if not self.payment.status_payment == Payment.PAYMENT_STATUS[1][1]:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não está Pago para ser cancelado.'}

        if user.has_perm('user.be_seller') and not user.is_superuser:
            if self.payment.payment_date + timezone.timedelta(minutes=int(user.seller.limit_time_to_cancel)) < tzlocal.now():
                return {'success':False,
                    'message':' Tempo limite para cancelar o Ticket '+ str(self.pk) +' excedido.'}

        if user.has_perm('user.be_manager') and not user.is_superuser:
            if self.payment.payment_date + timezone.timedelta(minutes=int(user.manager.limit_time_to_cancel)) < tzlocal.now():
                return {'success':False,
                    'message':' Tempo limite para cancelar o Ticket '+ str(self.pk) +' excedido.'}

        
        seller = self.payment.who_set_payment
        if not seller.can_sell_unlimited:
            seller.credit_limit += self.value
            seller.save()

        self.payment.status_payment = Ticket.TICKET_STATUS['Cancelado']
        self.payment.payment_date = None
        self.payment.seller_was_rewarded = True
        self.payment.save()
        self.save()

        TicketCancelationHistory.objects.create(who_cancelled=who_cancelled,
        ticket_cancelled=self,
        seller_of_payed=seller,
        store=Store.objects.first())

        return {'success':True,
            'message':'O Ticket '+ str(self.pk) +' foi cancelado.'}


    def validate_ticket(self, user):
        from history.models import SellerSalesHistory
        from core.models import Store                
        
        if self.cotation_sum() * self.value >= self.store.config.alert_bet_value:
            bet_reward_value = str(round((self.cotation_sum() * self.value),2))
            if self.store.email:
                subject = 'Alerta de aposta'
                message = 'Uma aposta com recompensa no valor de R$' + bet_reward_value + ' foi efetuada em sua plataforma'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [self.store.email,]
                send_mail( subject, message, email_from, recipient_list )\

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        if not self.payment.status_payment == Payment.PAYMENT_STATUS[0][1]:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não está Aguardando Pagamento.'}

        if not self.ticket_status == Ticket.TICKET_STATUS['Aguardando Resultados']:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não está Aguardando Resultados.'}


        for cotation in self.cotations.all():
            if cotation.game.start_date < tzlocal.now():
                return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não pode ser pago, pois tem jogo(s) que já começaram.'}


        seller_before_balance = 0
        seller_after_balance= 0
        if not user.seller.can_sell_unlimited:
            if self.value > user.seller.credit_limit:                
                return {'success':False,
                'message':'Você não tem saldo suficiente para pagar o Ticket: ' + str(self.pk)}
            seller_before_balance = user.seller.credit_limit
            user.seller.credit_limit -= self.value
            seller_after_balance = user.seller.credit_limit
            user.seller.save()
            
        self.seller = user.seller        
        self.save()
        self.payment.status_payment = Payment.PAYMENT_STATUS[1][1]
        self.payment.payment_date = tzlocal.now()
        self.payment.who_set_payment = Seller.objects.get(pk=user.pk)
        self.payment.save()

        SellerSalesHistory.objects.create(seller=user.seller,
        bet_ticket=self,
        value=self.value,
        seller_before_balance=seller_before_balance,
        seller_after_balance=seller_after_balance,
        store=self.store)
        
        return {'success':True,
            'message':'Ticket '+ str(self.pk) +' Pago com Sucesso. Ver <a href="/ticket/'+ str(self.pk) + '/">' + "Imprimir"+ '</a>'}


    def pay_winner_punter(self, user):
        from history.models import PunterPayedHistory

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        if self.reward.reward_status == Reward.REWARD_STATUS[1][1]:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' já foi recompensado.'}
        
        if not self.ticket_status == Ticket.TICKET_STATUS['Venceu']:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não Venceu'}

        if not self.payment.status_payment == Payment.PAYMENT_STATUS[1][1]:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não foi Pago.'}

        if not self.payment.who_set_payment.pk == user.pk:
            return {'success':False,
                'message':'Você só pode recompensar apostas pagas por você.'}

        if self.normal_user:
            punter_payed =  str(self.normal_user.pk) +' - '+ str(self.normal_user.first_name)
        elif self.user:
            punter_payed = str(self.user.pk) +' - '+ str(self.user.first_name)

        self.reward.reward_status = Reward.REWARD_STATUS[1][1]
        self.reward.reward_date = tzlocal.now()
        self.reward.who_rewarded = Seller.objects.get(pk=user.pk)
        self.reward.save()

        PunterPayedHistory.objects.create(punter_payed=punter_payed,
            seller=user.seller,
            ticket_winner=self,
            payed_value=self.reward.real_value)

        return {'success':True,
                'message':'O Apostador ' + punter_payed  + ' foi marcado como Pago'}


    def cotation_sum(self):
        from core.models import CotationHistory

        valid_cotations = CotationHistory.objects\
        .filter(ticket=self, game__game_status__in = (1,2,3,9))\
        .exclude(original_cotation__settlement=-1)
        
        cotation_sum = 1
        for cotation in valid_cotations:
            cotation_sum *= cotation.price
        if cotation_sum == 1:
            return 0

        from utils.models import GeneralConfigurations
        try:
            general_config = GeneralConfigurations.objects.get(pk=1)
            max_cotation_sum = general_config.max_cotation_sum
        except GeneralConfigurations.DoesNotExist:
            max_cotation_sum = 100000
        
        if cotation_sum > max_cotation_sum:
            cotation_sum = max_cotation_sum

        return round(cotation_sum,2)
    cotation_sum.short_description = 'Cota Total'


    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'        
        permissions = (
            ('can_validate_payment', "Can validate user ticket"),
            ('can_reward', "Can reward a user"),
        )


class Reward(models.Model):

    REWARD_STATUS = (
        ('Aguardando Resultados', 'Aguardando Resultados'),
        ('O apostador foi pago', 'O apostador foi pago'),
        ('Esse ticket não venceu', 'Esse ticket não venceu'),
        ('Venceu, Pagar Apostador', 'Venceu, Pagar Apostador'),
        ('Venceu, não pago','Venceu, não pago')
    )

    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_rewarded = models.ForeignKey('user.Seller', null=True, blank=True, on_delete=models.SET_NULL)
    reward_date = models.DateTimeField(null=True, blank=True)
    reward_status = models.CharField(max_length=80, choices=REWARD_STATUS, default=REWARD_STATUS[0][1], verbose_name='Status do Prêmio')

    @property
    def real_value(self):
        from utils.models import GeneralConfigurations, RewardRelated

        try:
            general_config = GeneralConfigurations.objects.get(pk=1)
            max_reward_to_pay = general_config.max_reward_to_pay
        except GeneralConfigurations.DoesNotExist:
            max_reward_to_pay = 50000


        reward_total = round(self.ticket.value * self.ticket.cotation_sum(), 2)


        for reward_related in RewardRelated.objects.all().order_by('value_max','pk'):
            if self.ticket.value <= reward_related.value_max and reward_total > reward_related.reward_value_max:
                if reward_total > reward_related.reward_value_max:
                    if reward_related.reward_value_max > max_reward_to_pay:
                        return max_reward_to_pay
                    else:
                        return reward_related.reward_value_max
                else:
                    if reward_total > max_reward_to_pay:
                        return max_reward_to_pay
                    else:
                        return reward_total

        if reward_total > max_reward_to_pay:
            return max_reward_to_pay
        else:
            return reward_total


    def __str__(self):
        return str(self.real_value)

    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'



class Payment(models.Model):

    PAYMENT_STATUS = (
        ('Aguardando Pagamento do Ticket', 'Aguardando Pagamento do Ticket'),
        ('Pago', 'Pago'),
        ('Cancelado', 'Cancelado'),
    )
    
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_set_payment = models.ForeignKey('user.Seller', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cambista')
    status_payment = models.CharField(max_length=80, choices=PAYMENT_STATUS, default=PAYMENT_STATUS[0][1], verbose_name='Status do Pagamento')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='Data do Pagamento')
    seller_was_rewarded = models.BooleanField(default=False, verbose_name='Cambista foi pago?')
    manager_was_rewarded = models.BooleanField(default=False, verbose_name='Gerente foi pago?')

    def __str__(self):
        return self.status_payment


    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

