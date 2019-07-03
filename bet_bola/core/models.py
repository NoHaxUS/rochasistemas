from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from user.models import TicketOwner
from django.conf import settings
from django.utils import timezone
import utils.timezone as tzlocal
from utils.models import GeneralConfigurations
from user.models import Seller
from ticket.models import Ticket
import utils.timezone as tzlocal

class Store(models.Model):
    fantasy = models.CharField(max_length=150, verbose_name="Nome da Banca")
    creation_date = models.DateTimeField(default=tzlocal.now, verbose_name="Data de Criação")
    email = models.EmailField(max_length=100,blank=True, null= True)

    def __str__(self):
        return self.fantasy + ' ID: ' + str(self.pk)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Banca'
        verbose_name_plural = 'Bancas'


class Game(models.Model):

    GAME_STATUS = (
        (0, 'Não Iniciado'),
        (1,'Ao Vivo'),
        (2, 'A ser corrigido') ,   
        (3, 'Terminado'),        
        (4, "Adiado"),
        (5, 'Cancelado'),
        (6, "W.O"),
        (7, "Interrompido"),
        (8, "Abandonado"),
        (9, "Retirado"),
        (99, "Removido"),
    )
    
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=100, verbose_name='Nome do Jogo')
    home_team = models.CharField(max_length=100, verbose_name='Time Casa')
    away_team = models.CharField(max_length=100, verbose_name='Time Fora')
    start_date = models.DateTimeField(verbose_name='Início da Partida')
    league = models.ForeignKey('League', related_name='my_games',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Liga')
    sport = models.ForeignKey('Sport', related_name='my_games',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Esporte')
    status = models.IntegerField(choices=GAME_STATUS,verbose_name='Status do Jogo')
    results_calculated = models.BooleanField(default=False, verbose_name='Resultados Calculados? ')
    available = models.BooleanField(default=True, verbose_name='Disponível?')
    can_be_modified_by_api = models.BooleanField(default=True, verbose_name='API pode modificar? ')

    @property
    def standard_cotations(self):
        return self.cotations.filter(market__name='1X2')


    def toggle_availability(self):
        self.available = not self.available
        self.save()
        
        return {
            'success': True,
            'message': 'Disponibilidade Alterada.'
        }


    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Jogo'
        verbose_name_plural = 'Jogos'


    def __str__(self):
        return self.name
    

class CotationModified(models.Model):
    cotation = models.ForeignKey('Cotation', related_name='my_modifiy', on_delete=models.CASCADE, verbose_name='Cota Original Modificada')
    store = models.ForeignKey('Store', related_name='my_modifiy', on_delete=models.CASCADE, verbose_name='Banca')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')    

    class Meta:
        ordering = ['-pk', ]
        verbose_name = 'Cota Modificada'
        verbose_name_plural = 'Cotas Modificadas'

class Cotation(models.Model):

    SETTLEMENT_STATUS = (
        (0, "Em Aberto"),
        (1, "Perdeu"),
        (2, "Ganhou"),
        (3, 'Ao Vivo')
    )

    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=120, verbose_name='Nome da Cota')
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')
    game = models.ForeignKey('Game', related_name='cotations', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Jogo')	
    settlement = models.IntegerField(default=0, choices=SETTLEMENT_STATUS, verbose_name="Resultado")
    market = models.ForeignKey('Market', related_name='cotations', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Tipo da Cota')
    total_goals = models.DecimalField(null=True, blank=True, max_digits=6, decimal_places=2, verbose_name='Total Acima/Abaixo')

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-pk', ]
        verbose_name = 'Cota'
        verbose_name_plural = 'Cotas'


class CotationCopy(models.Model):

    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    original_cotation = models.ForeignKey('Cotation', on_delete=models.CASCADE, verbose_name="Cotação Original", related_name='history_cotation')
    ticket = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Ticket', related_name='cotations_history')    
    price = models.DecimalField(max_digits=30, decimal_places=2, default=0, verbose_name='Valor Modificado')
    store = models.ForeignKey('core.Store', related_name='my_cotation_copies', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-pk',]
        verbose_name = 'Cota - Cópia'
        verbose_name_plural = 'Cotas - Cópia'


class Sport(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Cópia Cotação'
        verbose_name_plural = 'Cópia Cotações'


class League(models.Model):

    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=120, verbose_name='Nome', help_text='Campeonato')
    location = models.ForeignKey('Location', related_name='my_leagues',null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Local')
    priority = models.IntegerField(default=1, verbose_name='Prioridade')
    available = models.BooleanField(default=True, verbose_name="Visível?")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Liga'
        verbose_name_plural = 'Ligas'


class Location(models.Model):
    cc = models.CharField(max_length=5, verbose_name='CC', default='inter')
    name = models.CharField(max_length=45, verbose_name='Local')
    priority = models.IntegerField(default=1, verbose_name='Prioridade')
    available = models.BooleanField(default=True, verbose_name="Visível?")

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'País'
        verbose_name_plural = 'Países'


class Market(models.Model):
    name = models.CharField(max_length=100, verbose_name='Mercado', unique=True)
    available = models.BooleanField(default=True, verbose_name="Disponibilidade")
    
    def __str__(self):
        return str(self.name)
    
    def natural_key(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Mercado'
        verbose_name_plural = 'Mercados'
