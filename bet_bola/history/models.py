from django.db import models
from django.conf import settings


class TicketValidationHistory(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_validated = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_ticket_validations', verbose_name='Quem Validou')
    ticket = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Bilhete Validado')
    date = models.DateTimeField(verbose_name='Data da Validação')
    bet_value = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Apostado')
    balance_before = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior')
    balance_after = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Saldo Posterior')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-pk', ]
        verbose_name = 'Validação de Aposta'
        verbose_name_plural = 'Validações de Apostas'


class WinnerPaymentHistory(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    winner_name = models.CharField(max_length=200, verbose_name='Nome do Apostador')
    who_rewarded_the_winner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_payed_winner_tickets', on_delete=models.CASCADE, verbose_name='Cambista')
    ticket = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Bilhete Vencedor')
    date = models.DateTimeField(verbose_name='Data do Pagamento')
    bet_value = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Pago')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return "Pag. - Apostadores"

    class Meta:
        verbose_name = 'Pag. - Apostador'
        verbose_name_plural = 'Pag. - Apostadores'


class TicketCancelationHistory(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    who_cancelled = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='my_canceled_tickets', on_delete=models.CASCADE, verbose_name='Quem Cancelou ?')
    ticket = models.ForeignKey('ticket.Ticket', on_delete=models.CASCADE, verbose_name='Bilhete Cancelado')
    date = models.DateTimeField(verbose_name='Data do Cancelamento')
    who_paid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_canceled_tickets_who_i_paid', verbose_name='Quem Pagou o Ticket Cancelado')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return "Cancelamento de Bilhete"

    class Meta:
        verbose_name = 'Cancelamento de Bilhete'
        verbose_name_plural = 'Cancelamento de Bilhetes'


class ManagerTransactions(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    creditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_transactions",verbose_name='Gerente')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Cambista')
    transaction_date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    transferred_amount = models.DecimalField(max_digits=30, decimal_places=2,verbose_name='Valor Transferido')
    creditor_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior')
    creditor_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Atual')
    user_before_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Anterior(Cambista)')
    user_after_balance = models.DecimalField(max_digits=30, decimal_places=2,null=True,blank=True, verbose_name='Saldo Atual(Cambista)')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return " Transf. - Gerentes"

    class Meta:
        verbose_name = 'Transf. - Gerente'
        verbose_name_plural = 'Transf. - Gerentes'


class RevenueHistorySeller(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    register_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='quem prestou conta')
    tickets_registered = models.ManyToManyField('ticket.Ticket')
    seller = models.ForeignKey('user.Seller', on_delete=models.CASCADE, related_name="revenues", verbose_name='Cambista')
    date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    entry = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Entrada Total')
    comission = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='% Comissão')
    out = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='% Comissão')
    total_out = models.DecimalField(max_digits=40, decimal_places=2,null=True, blank=True, verbose_name='Saída Total')
    profit = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Lucro')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return "Pag. - Cambistas"

    class Meta:
        verbose_name = 'Pag. - Cambista'
        verbose_name_plural = 'Pag. - Cambistas'


class RevenueHistoryManager(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    register_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='quem prestou conta')
    tickets_registered = models.ManyToManyField('ticket.Ticket')
    manager = models.ForeignKey('user.Manager', on_delete=models.CASCADE, related_name="revenues",verbose_name='Gerente')
    date = models.DateTimeField(verbose_name='Data da Transação', auto_now_add=True)
    entry = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='Entrada Total')
    comission = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='% Comissão')
    out = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True, verbose_name='% Comissão')
    total_out = models.DecimalField(max_digits=40, decimal_places=2,null=True, blank=True, verbose_name='Saída Total')
    profit = models.DecimalField(max_digits=30, decimal_places=2,null=True, blank=True, verbose_name='Lucro')
    store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)


    def __str__(self):
        return "Pag. - Gerentes"

    class Meta:
        verbose_name = 'Pag. - Gerente'
        verbose_name_plural = 'Pag. - Gerentes'

