from django.db import models
from django.db.models import F, Q, When, Case
from django.db.models import Count, Sum
from django.utils import timezone
from user.models import Seller, Manager
from ticket.models import Ticket
from decimal import Decimal
from django.conf import settings
import utils.timezone as tzlocal


class Entry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Cambista')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    creation_date = models.DateTimeField(verbose_name='Data da Aposta', default=tzlocal.now)
    description = models.CharField(max_length=100, null=True, blank=True, verbose_name='Descrição')
    closed = models.BooleanField(default=False, verbose_name="Prestado conta?")
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)


class SellerComission(models.Model):
    seller_related = models.OneToOneField('user.Seller', null=True, blank=True, related_name="comissions", on_delete=models.CASCADE, verbose_name="Gerente Relacionado")    
    simple = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Simples")
    double = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Dupla")
    triple = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Tripla")
    fourth = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Quádrupla")
    fifth = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Quíntupla")
    sixth = models. DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Sêxtupla")
    sixth_more = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Mais de 6")
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Comissão do Gerentes"

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Comissão do Gerentes'
        verbose_name_plural = 'Comissões dos Gerentes'


class ManagerComission(models.Model):
    
    manager_related = models.OneToOneField('user.Manager', null=True, blank=True, related_name="comissions", on_delete=models.CASCADE, verbose_name="Cambista Relacionado")
    simple = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Simples")
    double = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Dupla")
    triple = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Tripla")
    fourth = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Quádrupla")
    fifth = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Quíntupla")
    sixth = models. DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Sêxtupla")
    sixth_more = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Mais de 6")
    profit_comission = models.DecimalField(max_digits=30, decimal_places=2,default=10, verbose_name="Comissão do lucro")
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Comissão do Cambista"

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Comissão do Cambista'
        verbose_name_plural = 'Comissões dos Cambistas'


class GeneralConfigurations(models.Model):
    store = models.OneToOneField('core.Store', on_delete=models.CASCADE, related_name='my_configuration')
    max_cotation_value = models.DecimalField(max_digits=30, decimal_places=2,default=200, verbose_name="Valor Máximo das Cotas")
    min_number_of_choices_per_bet = models.IntegerField(default=1, verbose_name="Número mínimo de escolhas por Aposta")
    max_number_of_choices_per_bet = models.IntegerField(default=50, verbose_name="Número máximo de escolhas por Aposta")
    max_reward_to_pay = models.DecimalField(max_digits=30, decimal_places=2,default=50000, verbose_name="Valor máximo pago pela Banca")
    min_bet_value = models.DecimalField(max_digits=30, decimal_places=2,default=1, verbose_name="Valor mínimo da aposta")
    max_bet_value = models.DecimalField(max_digits=30, decimal_places=2,default=1000000, verbose_name="Valor máximo da aposta")
    alert_bet_value = models.DecimalField(max_digits=30, decimal_places=2,default=1000, verbose_name="Valor de alerta para apostas")
    min_cotation_sum = models.DecimalField(max_digits=30, decimal_places=2,default=1, verbose_name="Valor mínimo da cota total")
    max_cotation_sum = models.DecimalField(max_digits=30, decimal_places=2, default=100000, verbose_name="Valor máximo da cota total")
    cotations_percentage = models.IntegerField(default=100, verbose_name="Ajuste das Cotas")
    block_bets = models.BooleanField(default=False, verbose_name="Bloquear Apostas?")
    bonus_won_ticket = models.BooleanField(default=False, verbose_name="Ativar Bônus por bilhetes premiados?")
    bonus_by_won_ticket = models.IntegerField(default=10, verbose_name="Bônus por bilhetes premiados")    


    def __str__(self):
        return "Configuração da Banca " + self.store.fantasy

    class Meta:
        ordering = ['-pk',]
        verbose_name = "Configurações Gerais"
        verbose_name_plural = "Configurações Gerais"


class RewardRestriction(models.Model):
    bet_value = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name="Valor da Aposta")
    max_reward_value = models.DecimalField(max_digits=30, decimal_places=2, default=100000, verbose_name="Valor Máximo da Recompensa")        
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Limitador de Prêmio"

    class Meta:
        ordering = ['-pk',]
        verbose_name = "Limitador de Prêmio"
        verbose_name_plural = "Limitador de Prêmios"


class TicketCustomMessage(models.Model):
    text = models.TextField(max_length=1000, verbose_name="Mensagem customizada", null=True, blank=True)
    store = models.OneToOneField('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Mensagem a ser mostrada no ticket"

    class Meta:
        ordering = ('-pk',)
        verbose_name = "Texto do Ticket"        
        verbose_name_plural = "Texto do Ticket" 


class RulesMessage(models.Model):
    text = models.TextField(max_length=999999, verbose_name="Texto de Regras", null=True, blank=True)
    store = models.OneToOneField('core.Store', verbose_name="Banca", on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return "Texto de Regras"

    class Meta:
        ordering = ('-pk',)
        verbose_name = "Texto de Regras"        
        verbose_name_plural = "Texto de Regras"



class MarketRemotion(models.Model):

    BELOW_ABOVE = (
        ("Abaixo", "Abaixo"),
        ("Acima","Acima")
    )
    
    MARKET_LIST = (
        (1,"Gols - Acima/Abaixo"),
        (2,"Total de Gols"),
        (3,"Resultado / Total de Gols"),
        (4,"Total de Gols / Ambos  Marcam"),
        (6,"Número de Gols na Partida"),
        (16,"Resultado 1° Tempo / Total de Gols"),
        (21,"Total de Gols 1° Tempo"),
        (29,"Total de Gols 2° Tempo"),

    )

    market_to_remove = models.IntegerField(choices=MARKET_LIST, verbose_name='Tipo de Aposta')
    under_above = models.CharField(max_length=8, choices=BELOW_ABOVE, verbose_name='Abaixo ou Acima')
    base_line = models.CharField(max_length=5, verbose_name='Valor')
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return self.get_market_to_remove_display() + ' - ' + self.under_above + ' ' +self.base_line

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Remoção de Aposta'
        verbose_name_plural = 'Remoção de Apostas'


class MarketModified(models.Model):
    market = models.ForeignKey('core.Market', verbose_name='Tipo de Aposta', related_name="my_modifications", on_delete=models.CASCADE)
    reduction_percentual = models.IntegerField(default=100, verbose_name='Percentual de Redução')
    available = models.BooleanField(default=True)
    modification_available = models.BooleanField(default=True)
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)


    def __str__(self):
        return str(self.reduction_percentual)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Redução de Cota'
        verbose_name_plural = 'Reduções de Cotas'


class ExcludedGame(models.Model):
    store = models.ForeignKey('core.Store', related_name='my_excluded_games', on_delete=models.CASCADE)
    game = models.ForeignKey('core.Game', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Jogo Removido'
        verbose_name_plural = 'Jogos Removidos'


class ExcludedLeague(models.Model):
    store = models.ForeignKey('core.Store', related_name='my_excluded_leagues', on_delete=models.CASCADE)
    league = models.ForeignKey('core.League', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Liga Removida'
        verbose_name_plural = 'Ligas Removidas'
