from django.db import models
from django.db.models import F, Q, When, Case
from django.db.models import Count, Sum
from django.utils import timezone
from user.models import Seller, Manager
from ticket.models import Ticket
from decimal import Decimal
from django.conf import settings
import utils.timezone as tzlocal


class Release(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Cambista')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    creation_date = models.DateTimeField(verbose_name='Data da Aposta', default=tzlocal.now)
    description = models.CharField(max_length=100, null=True, blank=True, verbose_name='Descrição')


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
    bonus_by_won_ticket = models.IntegerField(default=10, verbose_name="Bônus por bilhetes premiados")    
    auto_pay_winners = models.BooleanField(default=True, verbose_name="Auto Pagar Ganhadores")


    def __str__(self):
        return "Configuração Atual"

    def apply_reductions(self):
        from core.models import Game
        able_games = Game.objects.filter(start_date__gt=tzlocal.now(),
        status__in=[1,2,8,9],
        available=True)

        reduction = self.cotations_percentage / 100
        
        for game in able_games:
            game.cotations.update(price=F('price') * reduction )
            game.cotations.update(price=Case(When(price__lt=1,then=1.01),default=F('price')))
            game.cotations.filter(price__gt=self.max_cotation_value).update(price=self.max_cotation_value)


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
    text = models.TextField(max_length=1000, verbose_name="Mensagem customizada")
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Mensagem a ser mostrada no ticket"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save( *args, **kwargs)

    class Meta:
        verbose_name = "Texto do Ticket"        
        verbose_name_plural = "Texto do Ticket" 


class RulesMessage(models.Model):
    text = models.TextField(max_length=999999, verbose_name="Texto de Regras")
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Texto de Regras"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save( *args, **kwargs)

    class Meta:
        verbose_name = "Texto de Regras"        
        verbose_name_plural = "Texto de Regras"


class Overview(models.Model):
    overview = models.BooleanField(default=True, verbose_name='Gerar Visão Geral')
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)


    def total_revenue(self):
        sellers = Seller.objects.all()

        total_revenue_sum = 0
        for seller in sellers:
            total_revenue_sum += seller.actual_revenue()
        return total_revenue_sum
    total_revenue.short_description = 'Entrada Total'


    def total_out_money(self):

        sellers = Seller.objects.all()

        total_out_money_sum = 0
        for seller in sellers:
            total_out_money_sum += seller.out_money()
        return total_out_money_sum
    total_out_money.short_description = 'Saída Apostas'


    def seller_out_money(self):

        sellers = Seller.objects.filter(is_active=True)

        total_net_value_sum = 0
        for seller in sellers:
            total_net_value_sum += seller.net_value()
        
        return total_net_value_sum
    seller_out_money.short_description = 'Saída Cambistas'


    def manager_out_money(self):
        
        managers = Manager.objects.filter(is_active=True)

        total_net_value_sum = 0
        for manager in managers:
            total_net_value_sum += manager.net_value()
        
        return total_net_value_sum
    manager_out_money.short_description = 'Saída Gerentes'


    def total_net_value(self):
        return self.total_revenue() - (self.total_out_money() + self.seller_out_money() + self.manager_out_money())
    total_net_value.short_description = 'Lucro Total'


    def __str__(self):
        return "Visão Geral - Caixa"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save( *args, **kwargs)

    class Meta:
        verbose_name = "Visão Geral - Caixa"
        verbose_name_plural = "Visão Geral - Caixa"



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
        (17,"Resultado 1° Tempo / Total de Gols"),
        (22,"Total de Gols 1° Tempo"),
        (30,"Total de Gols 2° Tempo"),

    )

    market_to_remove = models.IntegerField(choices=MARKET_LIST, verbose_name='Tipo de Aposta')
    under_above = models.CharField(max_length=8, choices=BELOW_ABOVE, verbose_name='Abaixo ou Acima')
    base_line = models.CharField(max_length=5, verbose_name='Valor')
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return self.get_market_to_remove_display() + ' - ' + self.under_above + ' ' +self.base_line

    class Meta:
        verbose_name = 'Remoção de Aposta'
        verbose_name_plural = 'Remoção de Apostas'


class MarketReduction(models.Model):     

    market = models.ForeignKey('core.Market', verbose_name='Tipo de Aposta', related_name="my_reduction", on_delete=models.CASCADE)
    reduction_percentual = models.IntegerField(default=100, verbose_name='Percentual de Redução')
    active = models.BooleanField(default=True)
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)


    # def apply_reductions(self):
    #     from core.models import Game
        
    #     if GeneralConfigurations.objects.filter(pk=1):
    #         max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
    #     else:
    #         max_cotation_value = 200

    #     able_games = Game.objects.filter(start_date__gt=tzlocal.now(),
    #     status__in=[1,2,8,9],
    #     available=True)

    #     reduction = self.reduction_percentual / 100
        
    #     for game in able_games:

    #         if self.market_to_reduct == 600:
    #             cotations_to_reduct =  game.cotations.filter(market__id=1, name='Casa')
    #         elif self.market_to_reduct == 601:
    #             cotations_to_reduct =  game.cotations.filter(market__id=1, name='Empate')
    #         elif self.market_to_reduct == 602:
    #             cotations_to_reduct =  game.cotations.filter(market__id=1, name='Fora')
    #         else:
    #             cotations_to_reduct =  game.cotations.filter(market__id=self.market_to_reduct)
    #         cotations_to_reduct.update(price=F('price') * reduction )
    #         cotations_to_reduct.update(price=Case(When(price__lt=1,then=1.05),default=F('price')))
    #         cotations_to_reduct.filter(price__gt=max_cotation_value).update(price=max_cotation_value)    
            
    def __str__(self):
        return self.reduction_percentual


    class Meta:
        verbose_name = 'Redução de Cota'
        verbose_name_plural = 'Reduções de Cotas'


class ExcludedGame(models.Model):
    store = models.ForeignKey('core.Store', related_name='my_excluded_games', on_delete=models.CASCADE)
    game = models.ForeignKey('core.Game', on_delete=models.CASCADE)


class ExcludedLeague(models.Model):
    store = models.ForeignKey('core.Store', related_name='my_excluded_leagues', on_delete=models.CASCADE)
    league = models.ForeignKey('core.League', on_delete=models.CASCADE)
