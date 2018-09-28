from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from .manager import GamesManager, CotationsManager
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




class BetTicket(models.Model):

    BET_TICKET_STATUS = (
        ('Aguardando Resultados', 'Aguardando Resultados'),
        ('Não Venceu', 'Não Venceu'),
        ('Venceu', 'Venceu'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_bet_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Apostador')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_created_tickets', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Vendedor')
    normal_user = models.ForeignKey(NormalUser, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Cliente')
    cotations = models.ManyToManyField('Cotation', related_name='bet_ticket', verbose_name='Cota')
    creation_date = models.DateTimeField(verbose_name='Data da Aposta')
    reward = models.OneToOneField('Reward', related_name='ticket', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Recompensa')
    payment = models.OneToOneField('Payment', related_name='ticket', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Pagamento')
    value = models.DecimalField(max_digits=30, decimal_places=2, verbose_name='Valor Apostado')
    bet_ticket_status = models.CharField(max_length=80, choices=BET_TICKET_STATUS,default=BET_TICKET_STATUS[0][1],verbose_name='Status de Ticket')
    is_visible = models.BooleanField(default=True, verbose_name='Visível?')

    def __str__(self):
        return str(self.pk)

    def get_punter_name(self):
        if self.user:
            return self.user.first_name
        elif self.normal_user:
            return self.normal_user.first_name

    def hide_ticket(self):
        self.is_visible = False
        self.save()
        return {"message" :"Ticket "+ str(self.pk) +" Ocultado."}

    def get_ticket_link(self):
        from django.utils.safestring import mark_safe
        link = '<a href="/ticket/'+str(self.pk) + '/">Consultar<a/>'
        return mark_safe(link)
    get_ticket_link.short_description = 'Ver'

    def seller_related(self):
        if self.payment:
            return self.payment.who_set_payment
    seller_related.short_description = 'Vendedor'

    get_punter_name.short_description = 'Apostador'

    def cancel_ticket(self, user):
        from history.models import TicketCancelationHistory

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        who_cancelled  = str(user.pk) + ' - ' + user.username
        if not self.bet_ticket_status == 'Aguardando Resultados':
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
        self.payment.status_payment = 'Aguardando Pagamento do Ticket'
        self.payment.who_set_payment = None
        self.payment.payment_date = None
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

        if not self.bet_ticket_status == 'Aguardando Resultados':
            return {'success':False,
                'message':'O Ticket '+ str(self.pk) +' não está Aguardando Resultados.'}


        for cotation in self.cotations.all():
            if cotation.game.start_game_date < tzlocal.now():
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
        
        if self.reward.status_reward == 'O apostador foi pago':
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' já foi recompensado.'}

        if not self.payment or not self.reward:
            return {'success':False,
                'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
        
        if not self.bet_ticket_status == 'Venceu':
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

        self.reward.status_reward = Reward.REWARD_STATUS[1][1]
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
        valid_cotations = CotationHistory.objects.filter(bet_ticket=self, game__status_game__in = ('NS','FT','FT_PEN','AET','LIVE'))
        
        cotation_sum = 1
        for cotation in valid_cotations:
            cotation_sum *= cotation.value

        return round(cotation_sum,2)
    cotation_sum.short_description = 'Cota Total'


    def update_ticket_status(self):

        if self.cotations.filter(winning=False).count() > 0:
            self.bet_ticket_status = BetTicket.BET_TICKET_STATUS[1][1]
            self.reward.status_reward = Reward.REWARD_STATUS[2][1]
            self.reward.save()
            self.save()
        elif not self.cotations.filter(winning=None).count() > 0:
            self.bet_ticket_status = BetTicket.BET_TICKET_STATUS[2][1]
            self.reward.status_reward = Reward.REWARD_STATUS[3][1]
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

    original_cotation = models.IntegerField()
    bet_ticket = models.ForeignKey('BetTicket', on_delete=models.CASCADE, verbose_name='Ticket', related_name='cotations_history')
    name = models.CharField(max_length=80, verbose_name='Nome da Cota')
    original_value = models.DecimalField(max_digits=30, decimal_places=2,default=0,verbose_name='Valor Original')
    value = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')
    game = models.ForeignKey('Game', related_name='cotations_history', null=True,blank=True, on_delete=models.SET_NULL, verbose_name='Jogo')	
    winning = models.NullBooleanField(verbose_name='Vencedor ?')
    is_standard = models.BooleanField(default=False, verbose_name='Cota Padrão ?')
    kind = models.ForeignKey('Market', related_name='cotations_history', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Tipo da Cota')
    total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
  

class Game(models.Model):

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

    name = models.CharField(max_length=80, verbose_name='Nome do Jogo')
    start_game_date = models.DateTimeField(verbose_name='Início da Partida')
    championship = models.ForeignKey('Championship',related_name='my_games',null=True, blank=True, on_delete=models.SET_NULL,verbose_name='Campeonato')
    status_game = models.CharField(max_length=80,default=GAME_STATUS[0][1], choices=GAME_STATUS,verbose_name='Status do Jogo')
    ht_score = models.CharField(max_length=80, null=True, blank=True, verbose_name='Placar até o meio-tempo', help_text="Placar meio-tempo Ex: 3-5 (Casa-Visita)")
    ft_score = models.CharField(max_length=80, null=True, blank=True, verbose_name='Placar no final do Jogo', help_text="Placar final Ex: 3-5 (Casa-Visita)")
    odds_processed = models.BooleanField(default=False, verbose_name='Foi processado?')
    is_visible = models.BooleanField(default=True, verbose_name='Visível?')

    objects = GamesManager()	

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



class Championship(models.Model):

    name = models.CharField(max_length=80, verbose_name='Nome', help_text='Campeonato')
    country = models.ForeignKey('Country', related_name='my_championships',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Pais')
    priority = models.IntegerField(default=1, verbose_name='Prioridade')

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'Campeonato'
        verbose_name_plural = 'Campeonatos'


class Country(models.Model):

    name = models.CharField(max_length=45, verbose_name='País')
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
    )

    who_rewarded = models.ForeignKey('user.Seller', null=True, blank=True, on_delete=models.SET_NULL)
    reward_date = models.DateTimeField(null=True, blank=True)
    value = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    status_reward = models.CharField(max_length=80, choices=REWARD_STATUS, default=REWARD_STATUS[0][1], verbose_name='Status do Prêmio')

    @property
    def real_value(self):
        from utils.models import GeneralConfigurations

        try:
            general_config = GeneralConfigurations.objects.get(pk=1)
            max_reward_to_pay = general_config.max_reward_to_pay
        except GeneralConfigurations.DoesNotExist:
            max_reward_to_pay = 50000


        from core.views import get_max_reward_by_value
        max_value = get_max_reward_by_value(self.ticket.value, max_reward_to_pay)

        reward_total = round(self.ticket.value * self.ticket.cotation_sum(), 2)

        if reward_total > max_value:
            return max_value
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

    name = models.CharField(max_length=80, verbose_name='Nome da Cota')
    original_value = models.DecimalField(max_digits=30, decimal_places=2, default=0,verbose_name='Valor Original')
    value = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')
    game = models.ForeignKey('Game', related_name='cotations', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Jogo')	
    winning = models.NullBooleanField(verbose_name='Vencedor ?')
    is_standard = models.BooleanField(default=False, verbose_name='Cota Padrão ?')
    kind = models.ForeignKey(Market, related_name='cotations', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Tipo da Cota')
    total = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    objects = GamesManager()


    def __str__(self):
        return str(self.value)


    def save(self, *args, **kwargs):
        if Cotation.objects.filter(name=self.name, kind=self.kind, game=self.game).exists():
            Cotation.objects.filter(name=self.name, kind=self.kind, game=self.game)\
            .update(value=self.value, 
            original_value=self.original_value,
            total=self.total)
        else:
            if not is_excluded_cotation(self.name, self.kind):
                super().save(*args, **kwargs)

            
    class Meta:
        verbose_name = 'Cota'
        verbose_name_plural = 'Cotas'


class Payment(models.Model):

    PAYMENT_STATUS = (
        ('Aguardando Pagamento do Ticket', 'Aguardando Pagamento do Ticket'),
        ('Pago', 'Pago'),
    )

    who_set_payment = models.ForeignKey('user.Seller', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Vendedor')
    status_payment = models.CharField(max_length=80, choices=PAYMENT_STATUS, default=PAYMENT_STATUS[0][1], verbose_name='Status do Pagamento')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='Data do Pagamento')
    seller_was_rewarded = models.BooleanField(default=False, verbose_name='Vendedor foi pago?')
    manager_was_rewarded = models.BooleanField(default=False, verbose_name='Gerente foi pago?')

    def __str__(self):
        return self.status_payment


    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

