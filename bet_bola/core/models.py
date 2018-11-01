from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from user.models import Seller
from django.contrib.auth.models import User
from user.models import NormalUser
from django.utils import timezone
from django.db.models import Q
from user.models import NormalUser
from django.conf import settings
import utils.timezone as tzlocal
from .cotations_restrictions import is_excluded_cotation
from django.utils import timezone
import utils.timezone as tzlocal




class Ticket(models.Model):

    TICKET_STATUS = (
        ('Aguardando Resultados', 'Aguardando Resultados'),
        ('Não Venceu', 'Não Venceu'),
        ('Venceu', 'Venceu'),
        ('Venceu, não pago','Venceu, não pago'),
        ('Cancelado', 'Cancelado')
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Apostador')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_created_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cambista')
    normal_user = models.ForeignKey(NormalUser, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cliente')
    cotations = models.ManyToManyField('Cotation', related_name='ticket', verbose_name='Cota')
    creation_date = models.DateTimeField(verbose_name='Data da Aposta')
    reward = models.OneToOneField('Reward', related_name='ticket', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Recompensa')
    payment = models.OneToOneField('Payment', related_name='ticket', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Pagamento')
    value = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Valor Apostado')    
    is_visible = models.BooleanField(default=True, verbose_name='Visível?')

    def __str__(self):
        return str(self.pk)

    @property
    def ticket_status(self):         
        if self.payment.status_payment == 'Cancelado':
            return "Cancelado"   
        elif self.cotations.filter(~Q(status=3)).exclude(status=2):
            return "Aguardando Resultados"
        elif self.cotations.filter(~Q(settlement=2)).exclude(status=2).exclude(settlement=-1).exclude(settlement=3):
            return "Não Venceu"
        else:
            if self.payment.status_payment == 'Pago':
                return "Venceu"        
            return "Venceu e não foi pago"

    def get_punter_name(self):
        if self.user:
            return self.user.first_name
        elif self.normal_user:
            return self.normal_user.first_name
    get_punter_name.short_description = 'Apostador'

    def hide_ticket(self):
        self.is_visible = False
        self.save()
        return {"message" :"Ticket "+ str(self.pk) +" Ocultado."}

    def show_ticket(self):
        self.is_visible = True
        self.save()
        return {"message" :"Ticket "+ str(self.pk) +" Exibido."}

    def get_ticket_link(self):
        from django.utils.safestring import mark_safe
        link = '<a href="/ticket/'+str(self.pk) + '/">Consultar<a/>'
        return mark_safe(link)
    get_ticket_link.short_description = 'Ver'

    def seller_related(self):
        if self.payment:
            return self.payment.who_set_payment
    seller_related.short_description = 'Cambista'


    def cancel_ticket(self, user):
        from history.models import TicketCancelationHistory

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        who_cancelled  = str(user.pk) + ' - ' + user.username
        if not self.ticket_status == 'Aguardando Resultados':
            return {'success':False,
                'message':' Ticket '+ str(self.pk)+ ' não cancelado, pois não está aguardando resultados.'}
        
        if not self.payment.status_payment == 'Pago':
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não está Pago para ser cancelado.'}

        if user.has_perm('user.be_seller') and not user.is_superuser:
            if self.payment.payment_date + timezone.timedelta(minutes=int(user.seller.limit_time_to_cancel)) < tzlocal.now():
                return {'success':False,
                    'message':' Tempo limite para cancelar o Ticket '+ str(self.pk) +' excedido.'}

        

        seller = self.payment.who_set_payment
        seller.credit_limit += self.value
        seller.save()

        self.payment.status_payment = Ticket.TICKET_STATUS[4][1]
        self.payment.payment_date = None
        self.payment.seller_was_rewarded = True
        self.payment.save()
        self.save()

        TicketCancelationHistory.objects.create(who_cancelled=who_cancelled,
        ticket_cancelled=self,
        seller_of_payed=seller)

        return {'success':True,
            'message':'O Ticket '+ str(self.pk) +' foi cancelado.'}


    def validate_ticket(self, user):
        from history.models import SellerSalesHistory

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        if not self.payment.status_payment == 'Aguardando Pagamento do Ticket':
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não está Aguardando Pagamento.'}

        if not self.ticket_status == 'Aguardando Resultados':
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
        
        self.save()
        self.payment.status_payment = Payment.PAYMENT_STATUS[1][1]
        self.payment.payment_date = tzlocal.now()
        self.payment.who_set_payment = Seller.objects.get(pk=user.pk)
        self.payment.save()

        SellerSalesHistory.objects.create(seller=user.seller,
        bet_ticket=self,
        value=self.value,
        seller_before_balance=seller_before_balance,
        seller_after_balance=seller_after_balance)
        
        return {'success':True,
            'message':'Ticket '+ str(self.pk) +' Pago com Sucesso. Ver <a href="/ticket/'+ str(self.pk) + '/">' + "Imprimir"+ '</a>'}


    def pay_winner_punter(self, user):
        from history.models import PunterPayedHistory
        
        if self.reward.reward_status == 'O apostador foi pago':
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' já foi recompensado.'}

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        if not self.ticket_status == 'Venceu':
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não Venceu'}

        if not self.payment.status_payment == 'Pago':
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
        valid_cotations = CotationHistory.objects.filter(bet_ticket=self, game__game_status__in = (1,3,2))
        
        cotation_sum = 1
        for cotation in valid_cotations:
            cotation_sum *= cotation.price

        return round(cotation_sum,2)
    cotation_sum.short_description = 'Cota Total'


    def update_ticket_status(self):

        if self.cotations.filter(winning=False).count() > 0:
            self.ticket_status = Ticket.TICKET_STATUS[1][1]
            self.reward.status_reward = Reward.REWARD_STATUS[2][1]
            self.reward.save()
            self.save()
        elif not self.cotations.filter(winning=None).count() > 0:
            if self.payment.status_payment == 'Pago':
                self.ticket_status = Ticket.TICKET_STATUS[2][1]
                self.reward.status_reward = Reward.REWARD_STATUS[3][1]
            else:
                self.ticket_status = Ticket.TICKET_STATUS[3][1]
                self.reward.status_reward = Reward.REWARD_STATUS[4][1]
            self.reward.save()
            self.save()
            
            from utils.models import GeneralConfigurations
            if GeneralConfigurations.objects.filter(pk=1):
                auto_pay_punter = GeneralConfigurations.objects.get(pk=1).auto_pay_punter
            else:
                auto_pay_punter = False
            
            if auto_pay_punter and self.payment.who_set_payment:
                self.pay_winner_punter(self.payment.who_set_payment)


    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        permissions = (
            ('can_validate_payment', "Can validate user ticket"),
            ('can_reward', "Can reward a user"),
        )


class CotationHistory(models.Model):

    id = models.BigIntegerField(primary_key=True)
    original_cotation = models.BigIntegerField()
    bet_ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, verbose_name='Ticket', related_name='cotations_history')
    name = models.CharField(max_length=80, verbose_name='Nome da Cota')
    start_price = models.DecimalField(max_digits=30, decimal_places=2, default=0,verbose_name='Valor Original')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')
    game = models.ForeignKey('Game', related_name='cotations_history', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Jogo')	
    settlement = models.IntegerField(null=True, blank=True)
    status = models.IntegerField()
    market = models.ForeignKey('Market', related_name='cotations_history', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Tipo da Cota')
    line = models.CharField(max_length=30, null=True, blank=True)
    base_line = models.CharField(max_length=30, null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

 

class Sport(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Game(models.Model):

    GAME_STATUS = (
        (1, 'Não Iniciado'),
        (2,'Ao Vivo'),
        (3, 'Terminado') ,   
        (4, 'Cancelado'),        
        (5, "Adiado"),
        (6, 'Interrompindo'),
        (7, "Abandonado"),
        (8, "Pré-jogo")
    )

    name = models.CharField(max_length=80, verbose_name='Nome do Jogo')
    start_date = models.DateTimeField(verbose_name='Início da Partida')
    league = models.ForeignKey('League', related_name='my_games',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Liga')
    location = models.ForeignKey('Location', related_name='my_games',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Local')
    sport = models.ForeignKey('Sport', related_name='my_games',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Esporte')
    game_status = models.IntegerField(choices=GAME_STATUS,verbose_name='Status do Jogo')
    last_update = models.DateTimeField(verbose_name='Ultima Atualização')
    is_visible = models.BooleanField(default=True, verbose_name='Visível?')


    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Jogo'
        verbose_name_plural = 'Jogos'


    def __str__(self):
        return self.name

    def hide_game(self):
        self.is_visible = False
        self.save()
        return {"message" :"Jogo "+ str(self.pk) +" Ocultado."}


    def show_game(self):
        self.is_visible = True
        self.save()
        return {"message" :"Jogo "+ str(self.pk) +" Exibido."}


class Period(models.Model):
    
    PERIOD_STATUS = (
        (10,"Primeiro Tempo"),
        (20,"Segundo Tempo"),
        (30,"Primeiro Tempo (Prorrogacao)"),
        (35,"Segundo Tempo (Prorrogacao)"),
        (50,"Penaltis"),
        (100,"Termino"),
        (101,"Termino (Prorrogacao)"),
        (102,"Termino (Penaltis")
        )

    period_type = models.IntegerField(choices=PERIOD_STATUS)
    is_fineshed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    game = models.ForeignKey('Game',related_name='periods', on_delete=models.CASCADE)
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)


class League(models.Model):

    name = models.CharField(max_length=120, verbose_name='Nome', help_text='Campeonato')
    location = models.ForeignKey('Location', related_name='my_leagues',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Local')
    priority = models.IntegerField(default=1, verbose_name='Prioridade')

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'Liga'
        verbose_name_plural = 'Ligas'


class Location(models.Model):

    name = models.CharField(max_length=45, verbose_name='Local')
    priority = models.IntegerField(default=1, verbose_name='Prioridade')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'


class Reward(models.Model):

    REWARD_STATUS = (
        ('Aguardando Resultados', 'Aguardando Resultados'),
        ('O apostador foi pago', 'O apostador foi pago'),
        ('Esse ticket não venceu', 'Esse ticket não venceu'),
        ('Venceu, Pagar Apostador', 'Venceu, Pagar Apostador'),
        ('Venceu e não foi pago','Venceu e não foi pago')
    )

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
            if self.ticket.value <= reward_related.value_max:
                return reward_related.reward_value_max

        if reward_total > max_reward_to_pay:
            return max_reward_to_pay
        else:
            return reward_total



    def __str__(self):
        return str(self.real_value)

    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'


class Market(models.Model):

    name = models.CharField(max_length=100, verbose_name='Tipo de Aposta')
    
    def __str__(self):
        return str(self.name)
    
    def natural_key(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Aposta'
        verbose_name_plural = 'Tipo de Aposta'


class Cotation(models.Model):
    SETTLEMENT_STATUS = (
            (None, "Em Aberto"),
            (-1, "Cancelada"),
            (1, "Perdeu"),
            (2, "Ganhou"),
            (3, "Reembolso"),
            (4, "Metade Perdida"),
            (5, "Metade Ganha")
        )

    COTATION_STATUS = (
            (1,"Em aberto"),
            (2,"Suspensa"),
            (3, "Finalizada")
        )

    id = models.BigIntegerField(primary_key=True)
    id_string = models.CharField(max_length=40, default="")
    name = models.CharField(max_length=80, verbose_name='Nome da Cota')
    start_price = models.DecimalField(max_digits=30, decimal_places=2, default=0,verbose_name='Valor Original')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')
    game = models.ForeignKey('Game', related_name='cotations', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Jogo')	
    settlement = models.IntegerField(choices=SETTLEMENT_STATUS, null=True, blank=True)
    status = models.IntegerField(choices=COTATION_STATUS)
    market = models.ForeignKey('Market', related_name='cotations', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Tipo da Cota')
    line = models.CharField(max_length=30, null=True, blank=True)
    base_line = models.CharField(max_length=30, null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.price)


    # def save(self, *args, **kwargs):
    #     if not Cotation.objects.filter(name=self.name, market=self.market, game=self.game).exists():
    #         super().save(*args, **kwargs)

            
    class Meta:
        verbose_name = 'Cota'
        verbose_name_plural = 'Cotas'


class Payment(models.Model):

    PAYMENT_STATUS = (
        ('Aguardando Pagamento do Ticket', 'Aguardando Pagamento do Ticket'),
        ('Pago', 'Pago'),
        ('Cancelado', 'Cancelado'),
    )

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

