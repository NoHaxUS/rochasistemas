from django.db import models
from django.db.models import F, Q, When, Case


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

        super(GeneralConfigurations, self).save()


    class Meta:
        verbose_name = "Configurar Restrições"
        verbose_name_plural = "Configurar Restrições"


