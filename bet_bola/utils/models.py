from django.db import models
from django.db.models import F, Q, When, Case
from user.models import Seller, Manager
from core.models import Cotation


class GeneralConfigurations(models.Model):

    max_cotation_value = models.DecimalField(max_digits=30, decimal_places=2,default=200, verbose_name="Valor Máximo das Cotas")
    min_number_of_choices_per_bet = models.IntegerField(default=1, verbose_name="Número mínimo de escolhas por Aposta")
    max_reward_to_pay = models.DecimalField(max_digits=30, decimal_places=2,default=50000, verbose_name="Valor máximo pago pela Banca")
    min_bet_value = models.DecimalField(max_digits=30, decimal_places=2,default=1, verbose_name="Valor mínimo da aposta")
    percentual_reduction = models.IntegerField(default=100, verbose_name="Redução Percentual")

    def __str__(self):
        return "Configuração Atual"

    def save(self, *args, **kwargs):
        from core.models import Game
        
        self.pk = 1

        able_games = Game.objects.able_games()

        reduction = self.percentual_reduction / 100
        
        for game in able_games:
            game.cotations.update(value=F('original_value') * reduction )
            game.cotations.update(value=Case(When(value__lt=1,then=1.01),default=F('value')))
            game.cotations.filter(value__gt=self.max_cotation_value).update(value=self.max_cotation_value)

        super().save()


    class Meta:
        verbose_name = "Configurar Restrições"
        verbose_name_plural = "Configurar Restrições"



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
    seller_out_money.short_description = 'Gastos com Vendedores'


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
        verbose_name = "Visão Geral"
        verbose_name_plural = "Visão Geral"



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
        
        cotations_to_reduct =  Cotation.objects.filter(kind__id=self.market_to_reduct)

        cotations_to_reduct.update(value=F('original_value') * (self.reduction_percentual / 100) )
        cotations_to_reduct.update(value=Case(When(value__lt=1,then=1.05),default=F('value')))
        
        if GeneralConfigurations.objects.filter(pk=1):
            max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
        else:
            max_cotation_value = 200
        
        cotations_to_reduct.filter(value__gt=max_cotation_value).update(value=max_cotation_value)

    def save(self, *args, **kwargs):
        self.apply_reductions()
        super().save(args, kwargs)

    def __str__(self):
        return str(self.market_to_reduct)


    class Meta:
        verbose_name = 'Redução'
        verbose_name_plural = 'Reduções'


