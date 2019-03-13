from django.db import models
from django.db.models import F, Q, When, Case
from django.db.models import Count, Sum
from django.utils import timezone
from user.models import Seller, Manager
# from core.models import Cotation
from ticket.models import Ticket
from decimal import Decimal
import utils.timezone as tzlocal

class Comission(models.Model):
    
    seller_related = models.OneToOneField('user.Seller',related_name="comissions", on_delete=models.CASCADE, verbose_name="Cambista Relacionado")
    simple = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Simples")
    double = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Dupla")
    triple = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Tripla")
    fourth = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Quádrupla")
    fifth = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Quíntupla")
    sixth = models. DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Sêxtupla")
    sixth_more = models. DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="Mais de  6")


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
        return round(total_revenue * (self.triple / Decimal(100)),2)
    total_triple.short_description = "Tripla"

    def total_fourth(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count=4)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.fourth / Decimal(100)),2)
    total_fourth.short_description = "Quádrupla"


    def total_fifth(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count=5)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.fifth / Decimal(100)),2)
    total_fifth.short_description = "Quíntupla"


    def total_sixth(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count=6)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.sixth / Decimal(100)),2)
    total_sixth.short_description = "Sêxtupla"

    
    def total_sixth_more(self):
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(
            payment__who_set_payment=self.seller_related, 
            payment__seller_was_rewarded=False,
            ).annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=6)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
        return round(total_revenue * (self.sixth_more / Decimal(100)),2)
    total_sixth_more.short_description = "Mais de 6"
    

    def total_comission(self):
        return round(self.total_simple() + 
        self.total_double() + 
        self.total_triple() + 
        self.total_fourth() +
        self.total_fifth() +
        self.total_sixth() +
        self.total_sixth_more(),2)
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
    block_bets = models.BooleanField(default=False, verbose_name="Bloquear Apostas?")
    auto_pay_punter = models.BooleanField(default=True, verbose_name="Auto Pagar Apostadores")


    def __str__(self):
        return "Configuração Atual"

    def apply_reductions(self):
        from core.models import Game
        able_games = Game.objects.filter(start_date__gt=tzlocal.now(),
        game_status__in=[1,2,8,9],
        visible=True)

        reduction = self.percentual_reduction / 100
        
        for game in able_games:
            game.cotations.update(price=F('price') * reduction )
            game.cotations.update(price=Case(When(price__lt=1,then=1.01),default=F('price')))
            game.cotations.filter(price__gt=self.max_cotation_value).update(price=self.max_cotation_value)

    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(args, kwargs)


    class Meta:
        verbose_name = "Configurações Gerais"
        verbose_name_plural = "Configurações Gerais"


class RewardRelated(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    value_max = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name="Valor da Aposta")
    reward_value_max = models.DecimalField(max_digits=30, decimal_places=2, default=100000, verbose_name="Valor Máximo da Recompensa")        
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    def __str__(self):
        return "Limitador de Prêmio"

    class Meta:
        verbose_name = "Limitar Prêmios"
        verbose_name_plural = "Limitação de Prêmios"


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
        (2,"Abaixo/Acima"),
        (21,"Abaixo/Acima 1° Tempo"),
        (45,"Abaixo/Acima 2° Tempo"),
        (101,"Abaixo/Acima - Time de Casa"),
        (102,"Abaixo/Acima - Time de Fora")
    )

    market_to_remove = models.IntegerField(choices=MARKET_LIST, verbose_name='Tipo de Aposta')
    below_above = models.CharField(max_length=8, choices=BELOW_ABOVE, verbose_name='Abaixo ou Acima')
    base_line = models.CharField(max_length=5, verbose_name='Valor')
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)


    def __str__(self):
        return self.get_market_to_remove_display() + ' - ' + self.below_above + ' ' +self.base_line


    def save(self, *args, **kwargs):
        if not MarketRemotion.objects.filter(market_to_remove=self.market_to_remove, below_above=self.below_above, base_line=self.base_line).exists():
            super().save(args,kwargs)

    class Meta:
        verbose_name = 'Remoção de Aposta'
        verbose_name_plural = 'Remoção de Apostas'






class MarketReduction(models.Model):

    MARKET_LIST = (
        (600,"Casa"),
        (601,"Empate"),
        (602,"Fora"),
        (1,"1X2"),
        (2,"Abaixo/Acima"),
        (3,"Asian Handicap"),
        (4,"1° Tempo/2° Tempo"),
        (5,"Ímpar/Par"),
        (6,"Placar Correto"),
        (7,"Dupla Chance"),
        (9,"Placar Correto 1° Tempo"),
        #(11,"Total de Escanteios"),
        (13,"Handicap Europeu"),
        (16,"Primeiro Time a Marcar"),
        (17,"Ambos marcam?"),
        (21,"Abaixo/Acima 1° Tempo"),
        (25,"Dupla Chance 1° Tempo"),
        (41,"Vencedor 1° Tempo"),
        (42,"Vencedor 2° Tempo"),
        (45,"Abaixo/Acima 2° Tempo"),
        (52,"Casa/Fora"),
        (56,"Último time a marcar"),
        (61,"Handicap Europeu 1° Tempo"),
        (62,"Ímpar/Par 1° Tempo"),
        (64,"Asian Handicap 1° Tempo"),
        (71,"Metade com maior placar"),
        (73,"2° Tempo Ímpar/Par"),
        (79,"Haverá Pênalti?"),
        (84,"Vencer em ambas etapas"),
        (85,"Ganhar de Virada"),
        (86,"Vencer sem tomar Gol"),
        #(95,"Handicap - Escanteios"),
        (98,"Time de casa não toma gol?"),
        (99,"Time de fora não toma gol?"),
        (101,"Abaixo/Acima - Time de Casa"),
        (102,"Abaixo/Acima - Time de Fora"),
        (113,"Ambos marcam no 1° Tempo?"),
        (128,"Número de Gols"),
        #(129,"Abaixo/Acima Escanteios 1° Tempo"),
        (134,"Número de Gols 1° Tempo"),
        (143,"Em qual etapa o time de Casa vai fazer mais Gols?"),
        (144,"Em qual etapa o time de Fora vai fazer mais Gols?"),
        (149,"Número de gols Casa"),
        (150,"Número de Gols - Fora"),
        (161,"Resultado aos 10 minutos"),
        (163,"Número de Gols 2 ° Tempo"),
        (168,"Vai ter gol contra?"),
        (169,"Marcar em ambas etapas"),
        (171,"Ganhar uma ou ambas etapas"),
        (198,"Ímpar/Par - Time de Casa"),
        (199,"Ímpar/Par - Time de Fora"),
        (211,"Ambos marcam no 2° Tempo?"),
        (215,"Time de fora vai marcar no 1° Tempo?"),
        (216,"Time de fora vai marcar no 2° Tempo?"),
        (218,"Time de casa marca no 1° tempo?"),
        (219,"Time de casa marca 2° tempo?"),
        #(305,"Escanteios Abaixo/Exatamente/Acima"),
        (427,"Casa/Empate/Fora  Abaixo/Acima"),
        (429,"Vencedor do Encontro e Ambos Marcam"),
        (433,"European Handicap Corners"),
        (461,"Margem de Vitória"),
        (523,"Abaixo/Acima e Ambos marcam")
    )

    market_to_reduct = models.IntegerField(choices=MARKET_LIST, verbose_name='Tipo de Aposta', unique=True)
    reduction_percentual = models.IntegerField(default=100, verbose_name='Percentual de Redução')
    store = models.ForeignKey('core.Store', verbose_name="Banca", on_delete=models.CASCADE)

    """
    def reset_reducions(self):
        from core.models import Game

        if GeneralConfigurations.objects.filter(pk=1):
            max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
        else:
            max_cotation_value = 200

        able_games = Game.objects.filter(start_date__gt=tzlocal.now(),
        game_status__in=[1,2,8,9],
        visible=True)

        reduction = 1

        for game in able_games:
            
            if self.market_to_reduct == 600:
                cotations_to_reduct =  game.cotations.filter(market__id=1, name='Casa')
            elif self.market_to_reduct == 601:
                cotations_to_reduct =  game.cotations.filter(market__id=1, name='Empate')
            elif self.market_to_reduct == 602:
                cotations_to_reduct =  game.cotations.filter(market__id=1, name='Fora')
            else:
                cotations_to_reduct =  game.cotations.filter(market__id=self.market_to_reduct)
            cotations_to_reduct.update(price=F('price') * reduction )
            cotations_to_reduct.update(price=Case(When(price__lt=1,then=1.05),default=F('price')))
            cotations_to_reduct.filter(price__gt=max_cotation_value).update(price=max_cotation_value)
    """

    def apply_reductions(self):
        from core.models import Game
        
        if GeneralConfigurations.objects.filter(pk=1):
            max_cotation_value = GeneralConfigurations.objects.get(pk=1).max_cotation_value
        else:
            max_cotation_value = 200

        able_games = Game.objects.filter(start_date__gt=tzlocal.now(),
        game_status__in=[1,2,8,9],
        visible=True)

        reduction = self.reduction_percentual / 100
        
        for game in able_games:

            if self.market_to_reduct == 600:
                cotations_to_reduct =  game.cotations.filter(market__id=1, name='Casa')
            elif self.market_to_reduct == 601:
                cotations_to_reduct =  game.cotations.filter(market__id=1, name='Empate')
            elif self.market_to_reduct == 602:
                cotations_to_reduct =  game.cotations.filter(market__id=1, name='Fora')
            else:
                cotations_to_reduct =  game.cotations.filter(market__id=self.market_to_reduct)
            cotations_to_reduct.update(price=F('price') * reduction )
            cotations_to_reduct.update(price=Case(When(price__lt=1,then=1.05),default=F('price')))
            cotations_to_reduct.filter(price__gt=max_cotation_value).update(price=max_cotation_value)

    """
    def save(self, *args, **kwargs):
        self.apply_reductions()
        super().save(args, kwargs)
    """

    def __str__(self):
        return str(self.market_to_reduct)


    class Meta:
        verbose_name = 'Redução de Cota'
        verbose_name_plural = 'Reduções de Cotas'


