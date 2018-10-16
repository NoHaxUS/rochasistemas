from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
from django.db.models import F, Q, When, Case



class CustomUser(AbstractUser):
    cellphone = models.CharField(max_length=14, verbose_name='Celular')
    email = models.EmailField(null=True, blank=True, verbose_name='E-mail')

    def __str__(self):
        return self.username

    def full_name(self):
        return self.first_name + ' ' + self.last_name
    full_name.short_description = 'Nome Completo'

    


class NormalUser(models.Model):
    first_name = models.CharField(max_length=40, verbose_name='Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular')

    def __str__(self):
        return self.first_name


class Punter(CustomUser):	

    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = True
        
        super().save()
        
        self.define_default_permissions()

    def define_default_permissions(self):

        view_ticket_perm = Permission.objects.get(codename='view_betticket')
        be_punter = Permission.objects.get(codename='be_punter')
        change_punter = Permission.objects.get(codename='change_punter')

        self.user_permissions.add(view_ticket_perm, be_punter, change_punter)

    class Meta:
        verbose_name = 'Apostador'
        verbose_name_plural = 'Apostadores'

        permissions = (
            ('be_punter', 'Be a punter, permission.'),
        )



class Seller(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF', null=True, blank=True)
    address = models.CharField(max_length=75, verbose_name='Endereço', null=True, blank=True)
    can_sell_unlimited = models.BooleanField(default=False, verbose_name='Vender Ilimitado?')
    commission = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name='Comissão')
    credit_limit = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name='Créditos')
    my_manager = models.ForeignKey('Manager', on_delete=models.SET_NULL, related_name='manager_assoc', verbose_name='Gerente', null=True, blank=True)
    can_cancel_ticket = models.BooleanField(default=False, verbose_name='Cancela Bilhete ?')
    limit_time_to_cancel = models.FloatField(default=5, verbose_name="Tempo Limite de Cancelamento")

    def reset_revenue(self, who_reseted_revenue):
        from core.models import Payment
        from history.models import RevenueHistorySeller, PunterPayedHistory

        RevenueHistorySeller.objects.create(who_reseted_revenue=who_reseted_revenue,
        seller=self,
        final_revenue=self.actual_revenue(),
        actual_comission=self.commission,
        earned_value=self.net_value(),
        final_out_value=self.out_money(),
        profit = self.actual_revenue() - self.out_money())

        payments = Payment.objects.filter(who_set_payment=self, seller_was_rewarded=False)
        payments.update(seller_was_rewarded=True)

        payeds_open = PunterPayedHistory.objects.filter(seller=self, is_closed_for_seller=False)
        payeds_open.update(is_closed_for_seller=True)


    def full_name(self):
        return self.first_name + ' ' + self.last_name
    full_name.short_description = 'Nome Completo'

    
    def net_value(self):
        
        total_net_value = self.comissions.total_comission()
        return round(total_net_value, 2)

    net_value.short_description = 'A Receber'

    def real_net_value(self):
        return self.actual_revenue() -  (self.net_value() + self.out_money())
    real_net_value.short_description = 'Líquido'
    

    def see_comissions(self):
        from django.utils.html import format_html
        return format_html(
            '<a href="/admin/utils/comission/?q={}">Ver Comissões</a>',
            self.username,
        )
    see_comissions.short_description = 'Comissões'
    
    def get_commission(self):
        return str(round(self.commission,0)) + "%"
    get_commission.short_description = 'Comissão'

    def out_money(self):
        from history.models import PunterPayedHistory

        payed_sum = 0
        payeds_open = PunterPayedHistory.objects.filter(seller=self, is_closed_for_seller=False)

        for payed in payeds_open:
            payed_sum += payed.payed_value
        return payed_sum

    out_money.short_description = 'Pagamentos'


    def actual_revenue(self):

        from core.models import Ticket
        
        total_revenue = 0
        tickets_not_rewarded = Ticket.objects.filter(payment__who_set_payment=self, payment__seller_was_rewarded=False)
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value

        return total_revenue

    actual_revenue.short_description = 'Faturamento'


    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):			
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = True
        super().save()

        from utils.models import Comission
        comission = Comission.objects.filter(seller_related=self)
        if not comission:
            Comission(seller_related=self).save()
        self.define_default_permissions()

    def define_default_permissions(self):

        be_seller_perm = Permission.objects.get(codename='be_seller')
        change_ticket_perm = Permission.objects.get(codename='change_betticket')
        view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
        view_revenuehistoryseller_perm = Permission.objects.get(codename='view_revenuehistoryseller')
        view_sellersaleshistory_perm = Permission.objects.get(codename='view_sellersaleshistory')
        view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
        view_seller_perm = Permission.objects.get(codename='view_seller')
        view_punter_perm = Permission.objects.get(codename='view_punter')
        view_ticketcancelationhistory = Permission.objects.get(codename='view_ticketcancelationhistory')
        view_comission = Permission.objects.get(codename='view_comission')
        
        self.user_permissions.add(be_seller_perm, change_ticket_perm, 
        view_managertransactions_perm, view_revenuehistoryseller_perm, 
        view_sellersaleshistory_perm, view_punterpayedhistory_perm,
        view_seller_perm, view_punter_perm, view_ticketcancelationhistory, 
        view_comission)
 


    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Cambista'
        verbose_name_plural = 'Cambistas'

        permissions = (
            ('be_seller', 'Be a seller, permission.'),
        )



class Manager(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF', null=True, blank=True)
    address = models.CharField(max_length=75, verbose_name='Endereço', null=True, blank=True)
    commission = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name='Comissão')
    credit_limit_to_add = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name="Crédito")
    can_cancel_ticket = models.BooleanField(default=True, verbose_name='Cancela Bilhete ?')
    can_sell_unlimited = models.BooleanField(default=False, verbose_name='Vender Ilimitado?')

    def reset_revenue(self, who_reseted_revenue):
        from core.models import Payment
        from history.models import RevenueHistoryManager, PunterPayedHistory

        RevenueHistoryManager.objects.create(who_reseted_revenue=who_reseted_revenue,
        manager=self,
        final_revenue=self.actual_revenue(),
        actual_comission=self.commission,
        earned_value=self.net_value(),
        final_out_value=self.out_money(),
        profit = self.actual_revenue() - self.out_money())

        sellers = Seller.objects.filter(my_manager=self)
        for seller in sellers:
            payments_not_rewarded = Payment.objects.filter(who_set_payment=seller, manager_was_rewarded=False)
            payments_not_rewarded.update(manager_was_rewarded=True)
            payeds_open = PunterPayedHistory.objects.filter(seller=seller, is_closed_for_manager=False)
            payeds_open.update(is_closed_for_manager=True)


    def out_money(self):
        from history.models import PunterPayedHistory

        sellers = Seller.objects.filter(my_manager=self)

        payed_sum = 0
        for seller in sellers:
            payeds_open = PunterPayedHistory.objects.filter(seller=seller, is_closed_for_manager=False)

            for payed in payeds_open:
                payed_sum += payed.payed_value

        return payed_sum

    out_money.short_description = 'Pagamentos'


    def get_commission(self):
        return str(round(self.commission,0)) + "%"
    get_commission.short_description = 'Comissão'

    def net_value(self):
        total_net_value = self.actual_revenue() * (self.commission / 100)
        return round(total_net_value,2)
        
    net_value.short_description = 'A Receber'


    def real_net_value(self):
        return self.actual_revenue() -  (self.net_value() + self.out_money())
    
    real_net_value.short_description = 'Líquido'
    

    def actual_revenue(self):
        from core.models import Seller,Ticket

        sellers = Seller.objects.filter(my_manager=self)

        total_revenue = 0
        for seller in sellers:
            tickets_not_rewarded = Ticket.objects.filter(payment__who_set_payment=seller, payment__manager_was_rewarded=False)
            for ticket in tickets_not_rewarded:
                total_revenue += ticket.value
        return total_revenue

    actual_revenue.short_description = 'Faturamento'


    def manage_credit(self, obj, is_new=False):
        from history.models import ManagerTransactions

        seller = Seller.objects.get(pk=obj.pk)
        manager_before_balance = self.credit_limit_to_add

        if not self.can_sell_unlimited:
            if is_new:
                seller_before_balance = 0
                diff = obj.credit_limit
                seller_after_balance = obj.credit_limit
            else:
                seller_before_balance = seller.credit_limit
                diff = obj.credit_limit - seller.credit_limit
                seller_after_balance = seller.credit_limit + diff

            manager_balance_after = self.credit_limit_to_add - diff


            if manager_balance_after < 0:
                if is_new:
                    return {'success': False,
                    'message': 'Você não tem saldo suficiente para adicionar crédito, porém o cambista foi criado.'}
                else:
                    return {'success': False,
                    'message': 'Você não tem saldo suficiente.'}
            
            elif obj.credit_limit < 0:
                return {'success': False,
                'message': 'O cambista não pode ter saldo negativo.'}
            else:
                self.credit_limit_to_add -= diff
                self.save()

                if is_new:
                    seller.credit_limit = obj.credit_limit
                    seller.save()
        else:
            if obj.credit_limit < 0:
                return {'success': False,
                    'message': 'O cambista não pode ter saldo negativo.'}

            manager_balance_after = 0

            seller_before_balance = seller.credit_limit
            diff = obj.credit_limit - seller.credit_limit
            seller_after_balance = seller.credit_limit + diff

            self.save()

        if not self.can_sell_unlimited:
            if not manager_before_balance == manager_balance_after:
                ManagerTransactions.objects.create(manager=self,
                seller=seller,
                transferred_amount=diff,
                manager_before_balance=manager_before_balance,
                manager_after_balance=manager_balance_after,
                seller_before_balance=seller_before_balance,
                seller_after_balance=seller_after_balance)
        else:
            ManagerTransactions.objects.create(manager=self,
            seller=seller,
            transferred_amount=diff,
            manager_before_balance=manager_before_balance,
            manager_after_balance=manager_balance_after,
            seller_before_balance=seller_before_balance,
            seller_after_balance=seller_after_balance)

        return {'success': True,
            'message': 'Transação realizada.'}
        

    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = True
        super().save()

        self.define_default_permissions()

    def define_default_permissions(self):

        be_manager_perm = Permission.objects.get(codename='be_manager')
        view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
        view_revenuehistoryseller_perm = Permission.objects.get(codename='view_revenuehistoryseller')
        view_sellersaleshistory_perm = Permission.objects.get(codename='view_sellersaleshistory')
        view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
        view_revenuehistorymanager = Permission.objects.get(codename='view_revenuehistorymanager')
        change_seller = Permission.objects.get(codename='change_seller')
        add_seller = Permission.objects.get(codename='add_seller')
        view_manager = Permission.objects.get(codename='view_manager')
        view_ticket_perm = Permission.objects.get(codename='view_betticket')
        view_punter_perm = Permission.objects.get(codename='view_punter')
        change_ticket_perm = Permission.objects.get(codename='change_betticket')
        view_ticketcancelationhistory = Permission.objects.get(codename='view_ticketcancelationhistory')
        change_comission = Permission.objects.get(codename='change_comission')
        
        self.user_permissions.add(be_manager_perm,view_managertransactions_perm,
        view_revenuehistoryseller_perm,view_sellersaleshistory_perm,
        view_punterpayedhistory_perm, view_revenuehistorymanager, change_seller, add_seller,
        view_manager, view_ticket_perm, view_punter_perm, change_ticket_perm, 
        view_ticketcancelationhistory, change_comission)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
        permissions = (								
                ('be_manager', 'Be a manager, permission.'),
            )
