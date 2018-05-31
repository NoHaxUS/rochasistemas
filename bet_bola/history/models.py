from django.db import models
from django.conf import settings
from core.models import BetTicket
from user.models import Seller, Manager



class SellerSalesHistory(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    bet_ticket = models.ForeignKey(BetTicket, on_delete=models.CASCADE, verbose_name='Ticket Criado')
    sell_date = models.DateTimeField(verbose_name='Data da Venda', auto_now_add=True)
    value = models.FloatField(verbose_name='Valor Apostado')
    seller_before_balance = models.FloatField(null=True, verbose_name='Saldo Anterior')
    seller_after_balance = models.FloatField(null=True, verbose_name='Saldo Anterior')


    class Meta:
        verbose_name = 'Histórico - Vendedor'
        verbose_name_plural = 'Histórico - Vendedores'



class ManagerTransactions(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name='Gerente')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    transaction_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    transferred_amount = models.FloatField(verbose_name='Valor Transferido')
    seller_before_balance = models.FloatField(null=True, verbose_name='Saldo Anterior')
    seller_after_balance = models.FloatField(null=True, verbose_name='Saldo Atual')


    class Meta:
        verbose_name = 'Transação - Gerente'
        verbose_name_plural = 'Transações - Gerentes'


class RevenueHistorySeller(models.Model):
    who_reseted_revenue = models.CharField(max_length=200, verbose_name='Reponsável pelo Fechamento')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    revenue_reseted_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    final_revenue = models.FloatField(null=True, verbose_name='Faturamento')
    actual_comission = models.FloatField(null=True, verbose_name='Comissão')
    earned_value = models.FloatField(null=True, verbose_name='Valor Recebido')


    class Meta:
        verbose_name = 'Pagamentos - Vendedor'
        verbose_name_plural = 'Pagamentos - Vendedores'



class RevenueHistoryManager(models.Model):
    who_reseted_revenue = models.CharField(max_length=200, verbose_name='Reponsável pelo Fechamento')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name='Gerente')
    revenue_reseted_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    final_revenue = models.FloatField(null=True, verbose_name='Faturamento')
    actual_comission = models.FloatField(null=True, verbose_name='Comissão')
    earned_value = models.FloatField(null=True, verbose_name='Valor Recebido')


    class Meta:
        verbose_name = 'Pagamentos - Gerente'
        verbose_name_plural = 'Pagamentos - Gerentes'


