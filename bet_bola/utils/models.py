from django.db import models
from django.db.models import F, Q, When, Case
from django.db.models import Count
from django.utils import timezone
from user.models import Seller, Manager
from core.models import Cotation, Ticket
from decimal import Decimal
import utils.timezone as tzlocal

class Comission(models.Model):
    
    seller_related = models.OneToOneField('user.Seller',related_name="comissions", on_delete=models.CASCADE, verbose_name="Cambista Relacionado")
    simple = models.IntegerField(default=10, verbose_name="Apostas Simples")
    double = models.IntegerField(default=10, verbose_name="Apostas Duplas")
    triple_amount = models.IntegerField(default=10, verbose_name="Apostas Triplas")
    four_plus_amount = models.IntegerField(default=10, verbose_name="Mais de 3")


    def total_simple(self):
        
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count=1)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.simple / Decimal(100)),2)

    total_simple.short_description = "Simples"
    
    def total_double(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count=2)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.double / Decimal(100)),2)
    total_double.short_description = "Dupla"
    
    def total_triple(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count=3)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.triple_amount / Decimal(100)),2)
    total_triple.short_description = "Tripla"
    
    def total_plus(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=3)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.four_plus_amount / Decimal(100)),2)
    total_plus.short_description = "Mais que 3"
    

    def total_comission(self):
        return round(self.total_simple() + self.total_double() + self.total_triple() + self.total_plus(),2)
    total_comission.short_description = "Comissão Total"

    def __str__(self):
        return "Comissões dos Cambistas"

    class Meta:
        verbose_name = 'Comissão do Cambista'
        verbose_name_plural = 'Comissões dos Cambistas'

class GeneralConfigurations(models.Model):

    max_cotation_value = models.DecimalField(max_digits=30, decimal_places=2,default=200, verbose_name="Valor Máximo das Cotas")
    min_number_of_choices_per_bet = models.IntegerField(default=1, verbose_name="Número mínimo de escolhas por Aposta")
    max_reward_to_pay = models.DecimalField(max_digits=30, decimal_places=2,default=50000, verbose_name="Valor máximo pago pela Banca")
    min_bet_value = models.DecimalField(max_digits=30, decimal_places=2,default=1, verbose_name="Valor mínimo da aposta")
    max_bet_value = models.DecimalField(max_digits=30, decimal_places=2,default=1000000, verbose_name="Valor máximo da aposta")
    min_cotation_sum = models.DecimalField(max_digits=30, decimal_places=2,default=1, verbose_name="Valor mínimo da cota total")
    max_cotation_sum = models.DecimalField(max_digits=30, decimal_places=2, default=100000, verbose_name="Valor máximo da cota total")
    percentual_reduction = models.IntegerField(default=100, verbose_name="Redução Percentual")
    auto_pay_punter = models.BooleanField(default=False, verbose_name='Auto Pagar Vencedores')

    def __str__(self):
        return "Configuração Atual"

    def apply_reductions(self):
        from core.models import Game
        able_games =  games = Game.objects.filter(start_date__gt=tzlocal.now(), 
        start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
        game_status=1, 
        is_visible=True)

        reduction = self.percentual_reduction / 100
        
        for game in able_games:
            game.cotations.update(price=F('start_price') * reduction )
            game.cotations.update(price=Case(When(price__lt=1,then=1.01),default=F('price')))
            game.cotations.filter(price__gt=self.max_cotation_value).update(price=self.max_cotation_value)


    def save(self, *args, **kwargs):
        self.pk = 1
        self.apply_reductions()

        super().save(args, kwargs)


    class Meta:
        verbose_name = "Configurar Restrições"
        verbose_name_plural = "Configurar Restrições"


class RewardRelated(models.Model):
    value_max = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name="Valor da Aposta")
    reward_value_max = models.DecimalField(max_digits=30, decimal_places=2, default=100000, verbose_name="Valor Máximo da Recompensa")        

    class Meta:
        verbose_name = "Limitar Prêmios"
        verbose_name_plural = "Limitação de Prêmios"


class TicketCustomMessage(models.Model):
    text = models.TextField(max_length=75, verbose_name="Mensagem customizada")

    def __str__(self):
        return "Mensagem a ser mostrada no ticket"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save( *args, **kwargs)

    class Meta:
        verbose_name = "Mensagem a ser mostrada no ticket"        
        verbose_name_plural = "Mensagem a ser mostrada no ticket"


class RulesMessage(models.Model):
    text = models.TextField(max_length=999999, verbose_name="Texto de Regras")

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


    def total_revenue(self):
        sellers = Seller.objects.all()

        total_revenue_sum = 0
        for seller in sellers:
            total_revenue_sum += seller.actual_revenue()
        return total_revenue_sum
    total_revenue.short_description = 'Faturamento Total'


    def total_out_money(self):

        sellers = Seller.objects.all()

        total_out_money_sum = 0
        for seller in sellers:
            total_out_money_sum += seller.out_money()
        return total_out_money_sum
    total_out_money.short_description = 'Gastos com Apostas'


    def seller_out_money(self):

        sellers = Seller.objects.filter(is_active=True)

        total_net_value_sum = 0
        for seller in sellers:
            total_net_value_sum += seller.net_value()
        
        return total_net_value_sum
    seller_out_money.short_description = 'Gastos com Cambistas'


    def manager_out_money(self):
        
        managers = Manager.objects.filter(is_active=True)

        total_net_value_sum = 0
        for manager in managers:
            total_net_value_sum += manager.net_value()
        
        return total_net_value_sum
    manager_out_money.short_description = 'Gastos com Gerentes'


    def total_net_value(self):
        return self.total_revenue() - (self.total_out_money() + self.seller_out_money() + self.manager_out_money())
    total_net_value.short_description = 'Líquido Total'




    def __str__(self):
        return "Visão Geral"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save( *args, **kwargs)

    class Meta:
        verbose_name = "Visão Geral - Caixa"
        verbose_name_plural = "Visão Geral - Caixa"



class MarketReduction(models.Model):
    MARKET_LIST = (
        (1, "Vencedor do Encontro"),
        (10, "Casa/Visitante"),
        (37, "Vencedor do Primeiro Tempo"),
        (80, "Vencedor do Segundo Tempo"), 
        (976334, "Resultado/Total de Gol(s)"),
        (975916, "Resultado Exato no Primeiro Tempo"),
        (975909, "Resultado Exato do Jogo"),
        (976241, "Número Exato de Gol(s)"),
        (59, "Os Dois Times Marcam"),
        (976360, "Time Visitante Marca"),
        (976348, "Time da Casa Marca"),
        (976096, "Time da Casa NÃO Tomará Gol(s)"),
        (8594683, "Time Visitante NÃO Tomará Gol(s)"),
        (976204, "Total de Gols do Visitante"),
        (976198, "Total de Gols da Casa"),
        (12, "Total de Gol(s) no Encontro, Acima/Abaixo"),
        (47, "Total de Gol(s) no Segundo Tempo, Acima/Abaixo"),
        (38, "Total de Gols do Primeiro Tempo, Acima/Abaixo"),
        (976144, "Etapa com Mais Gol(s)"),
        (976316, "Resultado/2 Times Marcam"),
        (976193, "Vencedor nas Duas Etapas"),
        (63, "Dupla Chance"),
        (976236, "Vencer e não tomar Gol(s)"),
        (975930, "Placar Impar/Par"),
    )

    market_to_reduct = models.IntegerField(choices=MARKET_LIST, verbose_name='Tipo de Aposta', unique=True)
    reduction_percentual = models.IntegerField(default=100, verbose_name='Percentual de Redução')


    def apply_reductions(self):
        from core.models import Game
        able_games = Game.objects.filter(start_date__gt=tzlocal.now(), 
        start_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)),
        game_status=1, 
        is_visible=True)

        reduction = self.reduction_percentual / 100
        
        for game in able_games:

            cotations_to_reduct =  game.cotations.filter(kind__id=self.market_to_reduct)
            cotations_to_reduct.update(price=F('start_price') * reduction )
            cotations_to_reduct.update(price=Case(When(price__lt=1,then=1.05),default=F('price')))
            
            if GeneralConfigurations.objects.filter(pk=1):
                max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
            else:
                max_cotation_value = 200
            
            cotations_to_reduct.filter(price__gt=max_cotation_value).update(price=max_cotation_value)

    def save(self, *args, **kwargs):
        self.apply_reductions()
        super().save(args, kwargs)

    def __str__(self):
        return str(self.market_to_reduct)


    class Meta:
        verbose_name = 'Redução'
        verbose_name_plural = 'Reduções'


