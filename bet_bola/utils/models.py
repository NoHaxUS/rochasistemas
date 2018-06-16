from django.db import models
from django.db.models import F, Q, When, Case
from user.models import Seller


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
    total_out_money.short_description = 'Pagamentos Total'


    def total_net_value(self):

        sellers = Seller.objects.filter(is_active=True)

        total_net_value_sum = 0
        for seller in sellers:
            total_net_value_sum += seller.net_value()
        return total_net_value_sum
    total_net_value.short_description = 'Líquido Total'


    def profit_result(self):
        return self.total_revenue() - self.total_out_money()
    profit_result.short_description = 'Lucro Total'


    def __str__(self):
        return "Visão Geral"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save( *args, **kwargs)

    class Meta:
        verbose_name = "Visão Geral"
        verbose_name_plural = "Visão Geral"


