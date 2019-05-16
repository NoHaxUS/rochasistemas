from django.db import models
from django.conf import settings


class SellerSalesHistory(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    seller = models.ForeignKey('user.Seller', on_delete=models.CASCADE, verbose_name='Cambista')
    bet_ticket = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Bilhete Pago')
    sell_date = models.DateTimeField(verbose_name='Data da Venda', auto_now_add=True)
    value = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Apostado')
    seller_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior')
    seller_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Saldo Atual')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return "Entrada - Cambistas"


    class Meta:
        verbose_name = 'Entrada - Cambista'
        verbose_name_plural = 'Entradas - Cambistas'



class ManagerTransactions(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    manager = models.ForeignKey('user.Manager', on_delete=models.CASCADE, verbose_name='Gerente')
    seller = models.ForeignKey('user.Seller', on_delete=models.CASCADE, verbose_name='Cambista')
    transaction_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    transferred_amount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Transferido')
    manager_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior')
    manager_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Atual')
    seller_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior(Cambista)')
    seller_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Atual(Cambista)')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return " Transf. - Gerentes"

    class Meta:
        verbose_name = 'Transf. - Gerente'
        verbose_name_plural = 'Transf. - Gerentes'


class RevenueHistorySeller(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_reseted_revenue = models.CharField(max_length=200, verbose_name='Reponsável pelo Fechamento')
    seller = models.ForeignKey('user.Seller', on_delete=models.CASCADE, verbose_name='Cambista')
    revenue_reseted_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    final_revenue = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Entrada Total')
    earned_value = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Comissão')
    final_out_value = models.DecimalField(max_digits=40, decimal_places=2,null=True, blank=True, verbose_name='Saída Total')
    profit = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Lucro')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def get_commission(self):
        return str(round(self.actual_comission,0)) + "%"
    get_commission.short_description = '% de Comissão'


    def __str__(self):
        return "Pag. - Cambistas"

    class Meta:
        verbose_name = 'Pag. - Cambista'
        verbose_name_plural = 'Pag. - Cambistas'



class RevenueHistoryManager(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_reseted_revenue = models.CharField(max_length=200, verbose_name='Reponsável pelo Fechamento')
    manager = models.ForeignKey('user.Manager', on_delete=models.CASCADE, verbose_name='Gerente')
    revenue_reseted_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    final_revenue = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Entrada Total')
    actual_comission = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='% Comissão')
    earned_value = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Comissão')
    final_out_value = models.DecimalField(max_digits=40, decimal_places=2,null=True, blank=True, verbose_name='Saída Total')
    profit = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Lucro')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def get_commission(self):
        return str(round(self.actual_comission,0)) + "%"
    get_commission.short_description = '% de Comissão'


    def __str__(self):
        return "Pag. - Gerentes"

    class Meta:
        verbose_name = 'Pag. - Gerente'
        verbose_name_plural = 'Pag. - Gerentes'


class PunterPayedHistory(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    punter_payed = models.CharField(max_length=200, verbose_name='Apostador')
    seller = models.ForeignKey('user.Seller', on_delete=models.CASCADE, verbose_name='Cambista')
    ticket_winner = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Bilhete Vencedor')
    payment_date = models.DateTimeField(verbose_name='Data do Pagamento', auto_now_add=True)
    payed_value = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Pago')
    is_closed_for_seller = models.BooleanField(verbose_name='Cambista Prestou Conta?', default=False)
    is_closed_for_manager = models.BooleanField(verbose_name='Cambista Prestou Conta?', default=False)
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return "Pag. - Apostadores"

    class Meta:
        verbose_name = 'Pag. - Apostador'
        verbose_name_plural = 'Pag. - Apostadores'



class TicketCancelationHistory(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_cancelled = models.CharField(max_length=200, verbose_name='Quem Cancelou ?')
    ticket_cancelled = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Bilhete Cancelado')
    cancelation_date = models.DateTimeField(verbose_name='Data do Cancelamento')
    who_paid = models.ForeignKey('user.Seller', on_delete=models.CASCADE, verbose_name='Quem Pagou o Ticket')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return "Cancelamento de Bilhete"

    class Meta:
        verbose_name = 'Cancelamento de Bilhete'
        verbose_name_plural = 'Cancelamento de Bilhetes'

