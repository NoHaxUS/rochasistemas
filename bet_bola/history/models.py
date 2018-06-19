from django.db import models
from django.conf import settings
from core.models import BetTicket
from user.models import Seller, Manager



class SellerSalesHistory(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    bet_ticket = models.ForeignKey(BetTicket, on_delete=models.CASCADE, verbose_name='Ticket Pago')
    sell_date = models.DateTimeField(verbose_name='Data da Venda', auto_now_add=True)
    value = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Apostado')
    seller_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior')
    seller_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Saldo Atual')

    def __str__(self):
        return "Transações - Vendedores"


    class Meta:
        verbose_name = 'Transação - Vendedor'
        verbose_name_plural = 'Transações - Vendedores'



class ManagerTransactions(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name='Gerente')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    transaction_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    transferred_amount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Transferido')
    manager_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior')
    manager_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Atual')
    seller_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior(Vendedor)')
    seller_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Atual(Vendedor)')


    def __str__(self):
        return "Transações - Gerentes"

    class Meta:
        verbose_name = 'Transação - Gerente'
        verbose_name_plural = 'Transações - Gerentes'


class RevenueHistorySeller(models.Model):
    who_reseted_revenue = models.CharField(max_length=200, verbose_name='Reponsável pelo Fechamento')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    revenue_reseted_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    final_revenue = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Total Faturado')
    actual_comission = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Comissão')
    earned_value = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Valor Recebido')
    final_out_value = models.DecimalField(max_digits=40, decimal_places=2,null=True, blank=True, verbose_name='Total Pago')
    profit = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Lucro')


    def get_commission(self):
        return str(round(self.actual_comission,0)) + "%"
    get_commission.short_description = 'Comissão'


    def __str__(self):
        return "Pagamentos - Vendedores"

    class Meta:
        verbose_name = 'Pagamentos - Vendedor'
        verbose_name_plural = 'Pagamentos - Vendedores'



class RevenueHistoryManager(models.Model):
    who_reseted_revenue = models.CharField(max_length=200, verbose_name='Reponsável pelo Fechamento')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, verbose_name='Gerente')
    revenue_reseted_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    final_revenue = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Faturamento')
    actual_comission = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Comissão')
    earned_value = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Valor Recebido')
    final_out_value = models.DecimalField(max_digits=40, decimal_places=2,null=True, blank=True, verbose_name='Total Pago')
    profit = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Lucro')


    def get_commission(self):
        return str(round(self.actual_comission,0)) + "%"
    get_commission.short_description = 'Comissão'


    def __str__(self):
        return "Pagamentos - Gerentes"

    class Meta:
        verbose_name = 'Pagamentos - Gerente'
        verbose_name_plural = 'Pagamentos - Gerentes'


class PunterPayedHistory(models.Model):
    punter_payed = models.CharField(max_length=200, verbose_name='Apostador')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')
    ticket_winner = models.ForeignKey(BetTicket, on_delete=models.CASCADE, verbose_name='Ticket Vencedor')
    payment_date = models.DateTimeField(verbose_name='Data do Pagamento', auto_now_add=True)
    payed_value = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Pago')
    is_closed_for_seller = models.BooleanField(verbose_name='Vendedor Prestou Conta?', default=False)
    is_closed_for_manager = models.BooleanField(verbose_name='Gerente Prestou Conta?', default=False)

    def __str__(self):
        return "Pagamentos - Apostadores"

    class Meta:
        verbose_name = 'Pagamento - Apostador'
        verbose_name_plural = 'Pagamentos - Apostadores'



class TicketCancelationHistory(models.Model):
    who_cancelled = models.CharField(max_length=200, verbose_name='Quem Cancelou ?')
    ticket_cancelled = models.ForeignKey(BetTicket, on_delete=models.CASCADE, verbose_name='Ticket Cancelado')
    cancelation_date = models.DateTimeField(verbose_name='Data do Pagamento', auto_now_add=True)
    seller_of_payed = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Vendedor')

    def __str__(self):
        return "Cancelamento - Ticket"

    class Meta:
        verbose_name = 'Cancelamento - Ticket'
        verbose_name_plural = 'Cancelamentos - Tickets'
        
        
